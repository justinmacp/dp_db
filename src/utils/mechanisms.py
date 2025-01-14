import numpy as np
import pandas as pd

from src.utils import io
from src.utils.consts import ERROR_CODE, COUNT_SENSITIVITY, COMMA_STR, EMPTY_STR, DOUBLE_QUOTE_STR
from src.utils.helper import adjust_raw_histogram_to_specified_range
import streamlit as st


def laplace_mechanism(value, sensitivity: float, epsilon: float):
    scale = sensitivity / epsilon
    return np.random.laplace(value, scale)


def update_total_user_budget(epsilon: float, username: str, db: str):
    privacy_budget = (
        io.query_database(f"SELECT current_privacy_budget FROM users WHERE name = '{username}'", db)[0][0]
    )
    io.update_database(
        f"UPDATE users SET current_privacy_budget = {privacy_budget - epsilon} WHERE name = '{username}'",
        db,
        modify=True
    )


def count_with_laplacian_mechanism(epsilon: float, db: str, username: str) -> float:
    try:
        raw_result = io.query_database("SELECT COUNT(*) FROM passengers", db)[0][0]
        count = laplace_mechanism(raw_result, COUNT_SENSITIVITY, epsilon)
        update_total_user_budget(epsilon, username, db)
        return count
    except Exception as e:
        st.error('Query Failed: ', str(e))
        return ERROR_CODE


def sum_with_laplacian_mechanism(
        column: str, epsilon: float, lower_bound: int, upper_bound: int, db: str, username: str
) -> float:
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
            f"FROM passengers"
            f")",
            db
        )[0][0]
        total_sum = laplace_mechanism(raw_result, sensitivity, epsilon)
        update_total_user_budget(epsilon, username, db)
        return total_sum
    except Exception as e:
        st.error('Query Failed: ', str(e))
        return ERROR_CODE


def average_with_laplacian_mechanism(
        column: str, epsilon: float, lower_bound: int, upper_bound: int, db: str, username: str
) -> float:
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
            f"FROM passengers"
            f")",
            db
        )[0][0]
        average = laplace_mechanism(raw_result, sensitivity, epsilon)
        update_total_user_budget(epsilon, username, db)
        return average
    except Exception as e:
        st.error('Query Failed: ', str(e))
        return ERROR_CODE


def histogram_with_laplacian_mechanism(
        column: str, epsilon: float, lower_bound: int, upper_bound: int, bin_size: int, db: str, username: str
):
    """

    :param column:
    :param epsilon:
    :param lower_bound:
    :param upper_bound:
    :param bin_size:
    :param db:
    :param username:
    :return:
    """
    # TODO: bin size 0 needs an exception
    try:
        raw_result = io.query_database(
            f"WITH {column}Ranges AS ("
            f"WITH Clipped{column} AS ("
            f"SELECT CASE "
            f"WHEN {column} < {lower_bound} THEN {lower_bound} "
            f"WHEN {column} > {upper_bound} THEN {upper_bound} "
            f"ELSE {column} "
            f"END AS Clipped{column} "
            f"FROM passengers"
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
        update_total_user_budget(epsilon, username, db)
        return requested_histogram
    except Exception as e:
        st.error('Query Failed: ', str(e))
        return ERROR_CODE


def bar_chart_with_laplacian_mechanism(group_column: str, group_members: str, epsilon: float, db: str, username: str):
    try:
        raw_result = io.query_database(
            f"SELECT {group_column}, COUNT(*)  FROM passengers GROUP BY {group_column}", db
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
        update_total_user_budget(epsilon, username, db)
        return requested_bar_chart
    except Exception as e:
        st.error('Query Failed: ', str(e))
        return ERROR_CODE


def contingency_table_with_laplacian_mechanism(
        group_column_1: str,
        group_members_1: str,
        group_column_2: str,
        group_members_2: str,
        epsilon: float,
        db: str,
        username: str
):
    try:
        group_2_query = f""
        group_members_2_list = group_members_2.replace(DOUBLE_QUOTE_STR, EMPTY_STR).split(COMMA_STR)
        for member in group_members_2_list:
            group_2_query = group_2_query + f"COUNT(*) FILTER (WHERE {group_column_2} = {member}, "
        contingency_table = io.query_database(
            f"SELECT {group_column_1}, {group_2_query} FROM passengers GROUP BY {group_column_1}", db
        )
        contingency_table = contingency_table.apply(laplace_mechanism, args=(COUNT_SENSITIVITY, epsilon))
        update_total_user_budget(epsilon, username, db)
        return contingency_table
    except Exception as e:
        st.error('Query Failed: ', str(e))
        return ERROR_CODE
