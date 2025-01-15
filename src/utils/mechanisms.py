import numpy as np
import pandas as pd

from src.utils import io
from src.utils.consts import COUNT_SENSITIVITY, COMMA_STR, EMPTY_STR, DOUBLE_QUOTE_STR, TABLE_NAME
from src.utils.helper import adjust_raw_histogram_to_specified_range
import streamlit as st


def laplace_mechanism(value, sensitivity: float, epsilon: float):
    """
    Adds laplacian noise to a value according to query sensitivity and set epsilon.

    :param value: The value is the numerical base value that will be altered with noise. If an array type is specified
    it will add element wise noise.

    :param sensitivity: The sensitivity determined by the query type
    :param epsilon: The privacy budget specified by the user constrained by the available budget
    :return: The value altered by noise
    """
    scale = sensitivity / epsilon
    return np.random.laplace(value, scale)


def subtract_value_from_current_privacy_budget(subtrahend: float, username: str, db: str):
    """
    Retrieves current privacy budget of a user, subtracts a value and overwrites the current privacy budget

    :param subtrahend: The value to be subtracted. This is in the case of differential privacy, the budget that was used
    for the preceding query.
    :param username: The username of the user whose budget is updated. This requires usernames to be unique
    :param db: The file path to the database
    """
    privacy_budget = (
        io.query_database(f"SELECT current_privacy_budget FROM users WHERE name = '{username}'", db)[0][0]
    )
    io.update_database(
        f"UPDATE users SET current_privacy_budget = {privacy_budget - subtrahend} WHERE name = '{username}'",
        db,
        modify=True
    )


def count_with_laplacian_mechanism(epsilon: float, db: str, username: str, table_name: str = TABLE_NAME) -> float:
    """
    Counts the rows in a table with the laplacian mechanism.

    :param table_name: The name of the table
    :param epsilon: The privacy budget used for the mechanism
    :param username: The username of the user whois executing the query. This requires usernames to be unique
    :param db: The file path to the database
    :return: The differentially private count
    """
    try:
        raw_result = io.query_database(f"SELECT COUNT(*) FROM {table_name}", db)[0][0]
        count = laplace_mechanism(raw_result, COUNT_SENSITIVITY, epsilon)
        subtract_value_from_current_privacy_budget(epsilon, username, db)
        return count
    except Exception as e:
        st.error('Query Failed: ', str(e))


def sum_with_laplacian_mechanism(
        column: str,
        epsilon: float,
        lower_bound: float,
        upper_bound: float,
        db: str,
        username: str,
        table_name: str = TABLE_NAME
) -> float:
    """
    Calculates the sum over a column with the laplacian mechanism.

    :param column: The column to be aggregated over
    :param table_name: The name of the table
    :param epsilon: The privacy budget used for the mechanism
    :param username: The username of the user whois executing the query. This requires usernames to be unique
    :param db: The file path to the database
    :param lower_bound: The lower bound to which each value in the column will be clipped
    :param upper_bound: The upper bound to which each value in the column will be clipped
    :return: The differentially private sum
    """
    sensitivity = upper_bound - lower_bound
    try:
        raw_result = io.query_database(
            f"SELECT SUM(Clipped{column}) FROM "
            f"("
            f"SELECT CASE "
            f"WHEN {column} < {lower_bound} THEN {lower_bound} "
            f"WHEN {column} > {upper_bound} THEN {upper_bound} "
            f"ELSE {column} "
            f"END AS Clipped{column} "
            f"FROM {table_name}"
            f")", db)[0][0]
        total_sum = laplace_mechanism(raw_result, sensitivity, epsilon)
        subtract_value_from_current_privacy_budget(epsilon, username, db)
        return total_sum
    except Exception as e:
        st.error('Query Failed: ', str(e))


def average_with_laplacian_mechanism(
        column: str,
        epsilon: float,
        lower_bound: float,
        upper_bound: float,
        db: str,
        username: str,
        table_name: str = TABLE_NAME
) -> float:
    """
    Calculates the average over a column with the laplacian mechanism.

    :param column: The column to be aggregated over
    :param table_name: The name of the table
    :param epsilon: The privacy budget used for the mechanism
    :param username: The username of the user whois executing the query. This requires usernames to be unique
    :param db: The file path to the database
    :param lower_bound: The lower bound to which each value in the column will be clipped
    :param upper_bound: The upper bound to which each value in the column will be clipped
    :return: The differentially private average
    """
    sensitivity = COUNT_SENSITIVITY + upper_bound - lower_bound
    try:
        raw_result = io.query_database(
            f"SELECT AVG(Clipped{column}) FROM "
            f"("
            f"SELECT CASE "
            f"WHEN {column} < {lower_bound} THEN {lower_bound} "
            f"WHEN {column} > {upper_bound} THEN {upper_bound} "
            f"ELSE {column} "
            f"END AS Clipped{column} "
            f"FROM {table_name}"
            f")",
            db
        )[0][0]
        average = laplace_mechanism(raw_result, sensitivity, epsilon)
        subtract_value_from_current_privacy_budget(epsilon, username, db)
        return average
    except Exception as e:
        st.error('Query Failed: ', str(e))


def histogram_with_laplacian_mechanism(
        column: str,
        epsilon: float,
        lower_bound: float,
        upper_bound: float,
        bin_size: int,
        db: str,
        username: str,
        table_name: str = TABLE_NAME
):
    """
    Calculates the histogram over a column with the laplacian mechanism.

    :param column: The column to be aggregated over
    :param table_name: The name of the table
    :param epsilon: The privacy budget used for the mechanism
    :param username: The username of the user whois executing the query. This requires usernames to be unique
    :param db: The file path to the database
    :param lower_bound: The lower bound to which each value in the column will be clipped
    :param upper_bound: The upper bound to which each value in the column will be clipped
    :param bin_size: The bin size of the histogram
    :return: The differentially private histogram
    """
    try:
        raw_result = io.query_database(
            f"WITH {column}Ranges AS ("
            f"WITH Clipped{column} AS ("
            f"SELECT CASE "
            f"WHEN {column} < {lower_bound} THEN {lower_bound} "
            f"WHEN {column} > {upper_bound} THEN {upper_bound} "
            f"ELSE {column} "
            f"END AS Clipped{column} "
            f"FROM {table_name}"
            f") "
            f"SELECT "
            f"CAST(Clipped{column}/{bin_size} AS INTEGER)*{bin_size} As {column}Floor, "
            f"CAST(Clipped{column}/{bin_size} AS INTEGER)*{bin_size} + {bin_size - 1} As {column}Ceiling "
            f"FROM Clipped{column}"
            f") "
            f"SELECT "
            f"{column}Floor, "
            f"CONCAT(CAST({column}Floor AS INTEGER), ' to ', CAST({column}Ceiling AS INTEGER)) AS {column}Range, "
            f"COUNT(*) AS {column}Count "
            f"FROM {column}Ranges "
            f"GROUP BY {column}Floor, CONCAT(CAST({column}Floor AS INTEGER), ' to ', CAST({column}Ceiling AS INTEGER)) "
            f"ORDER BY {column}Floor",
            db
        )
        requested_histogram = adjust_raw_histogram_to_specified_range(raw_result, lower_bound, upper_bound, bin_size)
        requested_histogram = requested_histogram.apply(laplace_mechanism, args=(COUNT_SENSITIVITY, epsilon))
        subtract_value_from_current_privacy_budget(epsilon, username, db)
        return requested_histogram
    except Exception as e:
        st.error('Query Failed: ', str(e))


def bar_chart_with_laplacian_mechanism(
        column: str, group_members: str, epsilon: float, db: str, username: str, table_name: str = TABLE_NAME
):
    """
    Calculates the bar chart count over a column with the laplacian mechanism.

    :param group_members: A string of the categories to be created in the bar chart. These are comma separated and
    enclosed with double quotes
    :param column: The column to be aggregated over
    :param table_name: The name of the table
    :param epsilon: The privacy budget used for the mechanism
    :param username: The username of the user whois executing the query. This requires usernames to be unique
    :param db: The file path to the database
    :return: The differentially private histogram
    """
    try:
        raw_result = io.query_database(
            f"SELECT {column}, COUNT(*)  FROM {table_name} GROUP BY {column}",
            db
        )
        requested_category_names = group_members.replace(DOUBLE_QUOTE_STR, EMPTY_STR).split(COMMA_STR)
        requested_bar_chart = pd.DataFrame(
            data=[[0.0] * len(requested_category_names)], columns=requested_category_names
        )
        bar_chart = pd.DataFrame({x[0]: x[1:] for x in raw_result})
        for col in bar_chart.columns:
            if col in requested_bar_chart.columns:
                requested_bar_chart.at[0, col] = bar_chart.at[0, col]
        requested_bar_chart = (
            requested_bar_chart
            .apply(laplace_mechanism, args=(COUNT_SENSITIVITY, epsilon))
            .set_index(pd.Index(['Count']))
        )
        subtract_value_from_current_privacy_budget(epsilon, username, db)
        return requested_bar_chart
    except Exception as e:
        st.error('Query Failed: ', str(e))


def contingency_table_with_laplacian_mechanism(
        column_1: str,
        group_members_1: str,
        column_2: str,
        group_members_2: str,
        epsilon: float,
        db: str,
        username: str,
        table_name: str = TABLE_NAME
):
    """
    Calculates the bar chart count over a column with the laplacian mechanism.

    :param group_members_1: A string of the categories to be created as columns in the contingency table. These are
    comma separated and enclosed with double quotes
    :param column_1: The column to be aggregated over as columns in the contingency table
    :param group_members_2: A string of the categories to be created as rows in the contingency table. These are comma
    separated and enclosed with double quotes
    :param column_2: The column to be aggregated over as rows in the contingency table
    :param table_name: The name of the table
    :param epsilon: The privacy budget used for the mechanism
    :param username: The username of the user whois executing the query. This requires usernames to be unique
    :param db: The file path to the database
    :return: The differentially private histogram
    """
    try:
        group_2_query = f""
        group_members_2_list = group_members_2.replace(DOUBLE_QUOTE_STR, EMPTY_STR).split(COMMA_STR)
        for member in group_members_2_list:
            group_2_query = group_2_query + f"COUNT(*) FILTER (WHERE {column_2} = {member}, "
        contingency_table = io.query_database(
            f"SELECT {column_1}, {group_2_query} FROM {table_name} GROUP BY {column_1}", db)
        contingency_table = contingency_table.apply(laplace_mechanism, args=(COUNT_SENSITIVITY, epsilon))
        subtract_value_from_current_privacy_budget(epsilon, username, db)
        return contingency_table
    except Exception as e:
        st.error('Query Failed: ', str(e))
