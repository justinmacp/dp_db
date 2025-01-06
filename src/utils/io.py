import pandas as pd
import sqlite3
from src.utils.consts import NUMERIC_TYPE_COLUMNS, DATABASE


def read_data(file: str) -> pd.DataFrame:
    df = pd.read_csv(file)
    return df


def query_database(query, database):
    """Runs a query on the SQLite database."""
    connector = sqlite3.connect(database)
    cursor = connector.cursor()
    cursor.execute(query)
    result = cursor.fetchone()[0]
    connector.close()
    return result


def update_database(query, db, params=None, modify=False):
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    try:
        if modify:
            cursor.execute(query, params or ())
            conn.commit()  # Commit changes for UPDATE/INSERT/DELETE
            return None
        else:
            cursor.execute(query, params or ())
            return cursor.fetchall()
    finally:
        conn.close()


def get_column_names(table_name, database):
    numeric_columns = []
    connector = sqlite3.connect(database)
    cursor = connector.cursor()
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    for col in columns:
        if any(keyword in col[2].upper() for keyword in NUMERIC_TYPE_COLUMNS):
            numeric_columns.append(col[1])
    return numeric_columns


def reset_privacy_budgets():
    update_database(f"UPDATE users SET current_privacy_budget = max_privacy_budget", DATABASE, modify=True)
