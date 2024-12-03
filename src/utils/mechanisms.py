import numpy as np
from src.utils import io


def laplace_mechanism(value: float, sensitivity: float, epsilon: float) -> float:
    scale = sensitivity / epsilon
    return np.random.laplace(value, scale)


def update_total_user_budget(epsilon: float, username: str, db: str):
    privacy_budget = io.query_database(f"SELECT current_privacy_budget FROM USERS WHERE name = '{username}'", db)
    io.update_database(
        f"UPDATE USERS SET current_privacy_budget = {privacy_budget - epsilon} WHERE name = '{username}'",
        db,
        modify=True
    )


def count_with_laplacian_mechanism(epsilon: float, db: str, username: str) -> float:
    sensitivity = 1
    try:
        raw_result = io.query_database("SELECT COUNT(*) FROM passengers", db)
        count = laplace_mechanism(raw_result, sensitivity, epsilon)
        update_total_user_budget(epsilon, username, db)
        return count
    except Exception as e:
        print('Query Failed: ', str(e))
        return -1


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
        )
        total_sum = laplace_mechanism(raw_result, sensitivity, epsilon)
        update_total_user_budget(epsilon, username, db)
        return total_sum
    except Exception as e:
        print('Query Failed: ', str(e))
        return -1


def average_with_laplacian_mechanism(
        column: str, epsilon: float, lower_bound: int, upper_bound: int, db: str, username: str
) -> float:
    sensitivity = 1 + upper_bound - lower_bound
    try:
        raw_result = io.query_database(
            f"SELECT AVG(clipped_column) FROM "
            f"("
            f"SELECT CASE "
            f"WHEN {column} < {lower_bound} THEN {lower_bound} "
            f"WHEN {column} > {upper_bound} THEN {upper_bound} "
            f"ELSE {column} "
            f"END AS clipped_column "
            f"FROM passengers"
            f")",
            db
        )
        average = laplace_mechanism(raw_result, sensitivity, epsilon)
        update_total_user_budget(epsilon, username, db)
        return average
    except Exception as e:
        print('Query Failed: ', str(e))
        return -1
