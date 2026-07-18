import os
import json
import psycopg2
from dotenv import load_dotenv

load_dotenv()
db_url = os.getenv("DATABASE_URL")

conn = psycopg2.connect(db_url)
conn.autocommit = True
cur = conn.cursor()

data = {}

for table in ["raw_price_history", "mf_assets_value_change", "raw_mutual_funds"]:
    cur.execute(f"""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = '{table}';
    """)
    cols = cur.fetchall()
    data[table] = [row[0] for row in cols]

with open('temp/db_scan_results2.json', 'w') as f:
    json.dump(data, f, indent=2)

conn.close()
