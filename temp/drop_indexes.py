import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
db_url = os.environ.get("DATABASE_URL")
if not db_url:
    print("DATABASE_URL not found")
    exit(1)

conn = psycopg2.connect(db_url)
conn.autocommit = True
cur = conn.cursor()

commands = [
    "DROP INDEX IF EXISTS public.idx_raw_mf_nepsealpha_assets_lastmonth_symbol;",
    "DROP INDEX IF EXISTS public.idx_raw_mf_nepsealpha_assets_lastmonth_month;",
    "DROP INDEX IF EXISTS public.idx_raw_price_history_date;",
    "DROP INDEX IF EXISTS public.idx_fundamental_data_date;"
]

for cmd in commands:
    print(f"Executing: {cmd}")
    cur.execute(cmd)

print("Indexes dropped successfully.")
cur.close()
conn.close()
