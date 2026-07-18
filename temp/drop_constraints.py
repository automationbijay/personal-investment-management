import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
db_url = os.getenv("DATABASE_URL")

conn = psycopg2.connect(db_url)
conn.autocommit = True
cur = conn.cursor()

constraints_to_drop = [
    ("raw_securities", "raw_securities_symbol_key"),
    ("fundamental_data", "fundamental_data_symbol_key"),
    ("raw_price_history", "unique_symbol_date")
]

for table, constraint in constraints_to_drop:
    try:
        cur.execute(f"ALTER TABLE public.{table} DROP CONSTRAINT IF EXISTS {constraint};")
        print(f"Dropped constraint: {constraint} on {table}")
    except Exception as e:
        print(f"Error dropping constraint {constraint} on {table}: {e}")

conn.close()
print("Constraint modifications complete.")
