import pandas as pd
import sqlite3
from src.utils.consts import TABLE_NAME, DATABASE, RAW_DATA

# Step 1: Load the CSV file
data = pd.read_csv(RAW_DATA)

# Step 2: Connect to SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect(DATABASE)

# Step 3: Write the DataFrame to a new SQLite table
data.to_sql(TABLE_NAME, conn, if_exists='replace', index=False)

# Step 4: Close the connection
conn.close()

print(f"Data from {RAW_DATA} has been successfully written to {DATABASE} in table '{TABLE_NAME}'.")
