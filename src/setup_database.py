import pandas as pd
import sqlite3

# Step 1: Load the CSV file
csv_file = '../data/train.csv'  # Replace with your CSV file path
data = pd.read_csv(csv_file)

# Step 2: Connect to SQLite database (or create it if it doesn't exist)
db_name = '../data/titanic.db'  # Replace with your database name
conn = sqlite3.connect(db_name)

# Step 3: Write the DataFrame to a new SQLite table
table_name = 'passengers'  # Replace with your table name
data.to_sql(table_name, conn, if_exists='replace', index=False)

# Step 4: Close the connection
conn.close()

print(f"Data from {csv_file} has been successfully written to {db_name} in table '{table_name}'.")
