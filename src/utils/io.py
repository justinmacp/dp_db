import pandas as pd
import sqlite3


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
