import sqlite3
from src.utils.consts import DATABASE


def query_database(query: str, db: str):
    """Runs a query on the SQLite database.

    :param query: The query as a string. This is typically the query written in SQL
    :param db: The file path to the database
    :return: The result to the query
    """
    connector = sqlite3.connect(db)
    cursor = connector.cursor()
    cursor.execute(query)
    result = cursor.fetchall()
    connector.close()
    return result


def update_database(query: str, db: str, modify: bool = False):
    """
    Implements Manipulation of a table in a database.

    :param query: The query as a string. This is typically the query written in SQL
    :param db: The file path to the database
    :param modify: A flag whether the data should be modified or not
    :return: Returns the result of the query
    """
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    try:
        if modify:
            cursor.execute(query, ())
            conn.commit()
            return None
        else:
            cursor.execute(query, ())
            return cursor.fetchall()
    finally:
        conn.close()


def reset_privacy_budgets():
    """
    Resets the privacy budget of all users registered to the service to their max budget. This implements a simple
    subscription model, where the budget of each user is reset after a certain period. This function can be scheduled
    via a script in a productive environment.
    """
    update_database(f"UPDATE users SET current_privacy_budget = max_privacy_budget", DATABASE, modify=True)
