import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
db_url = os.environ.get("DATABASE_URL")
if not db_url:
    print("DATABASE_URL not found")
    exit(1)

conn = psycopg2.connect(db_url)
cur = conn.cursor()

cur.execute("""
    SELECT c.relname as view_name, c.reloptions
    FROM pg_class c
    JOIN pg_namespace n ON n.oid = c.relnamespace
    WHERE n.nspname = 'public' AND c.relkind = 'v'
    AND c.relname IN ('mf_assets_value_change', 'vw_mf_summary_analytics');
""")

for row in cur.fetchall():
    print(row)

cur.close()
conn.close()
