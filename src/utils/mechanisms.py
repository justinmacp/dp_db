import numpy as np
from src.utils import io
from src.utils.consts import ERROR_CODE, COUNT_SENSITVITY


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
    sensitivity = COUNT_SENSITVITY
    try:
        raw_result = io.query_database("SELECT COUNT(*) FROM passengers", db)[0][0]
        count = laplace_mechanism(raw_result, sensitivity, epsilon)
        update_total_user_budget(epsilon, username, db)
        return count
    except Exception as e:
        print('Query Failed: ', str(e))
        return ERROR_CODE


def sum_with_laplacian_mechanism(
        column: str, epsilon: float, lower_bound: int, upper_bound: int, db: str, username: str
) -> float:
    sensitivity = upper_bound - lower_bound
    try:
        raw_result = io.query_database(
            f"SELECT SUM(clipped_column) FROM "
            f"("
            f"SELECT CASE "
            f"WHEN {column} < {lower_bound} THEN {lower_bound} "
            f"WHEN {column} > {upper_bound} THEN {upper_bound} "
            f"ELSE {column} "
            f"END AS clipped_column "
            f"FROM passengers"
            f")",
            db
        )[0][0]
        total_sum = laplace_mechanism(raw_result, sensitivity, epsilon)
        update_total_user_budget(epsilon, username, db)
        return total_sum
    except Exception as e:
        print('Query Failed: ', str(e))
        return ERROR_CODE


def average_with_laplacian_mechanism(
        column: str, epsilon: float, lower_bound: int, upper_bound: int, db: str, username: str
) -> float:
    sensitivity = COUNT_SENSITVITY + upper_bound - lower_bound
    try:
        raw_result = io.query_database(
            f"SELECT AVG(clipped_column) FROM "
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
        print('Query Failed: ', str(e))
        return ERROR_CODE


def histogram_with_laplacian_mechanism(
        column: str, epsilon: float, lower_bound: int, upper_bound: int, bin_size: int, db: str, username: str
):
    sensitivity = COUNT_SENSITVITY
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
            f"CONCAT({column}Floor, ' to ', {column}Ceiling) AS {column}Range, "
            f"COUNT(*) AS {column}Count "
            f"FROM {column}Ranges "
            f"GROUP BY {column}Floor, CONCAT({column}Floor, ' to ', {column}Ceiling) "
            f"ORDER BY {column}Floor",
            db
        )
        print(raw_result)

        raw_result = np.array(raw_result)[:, 2].astype('float')
        print(raw_result)
        average = laplace_mechanism(raw_result, sensitivity, epsilon)
        print(average)
        update_total_user_budget(epsilon, username, db)
        return average
    except Exception as e:
        print('Query Failed: ', str(e))
        return []
