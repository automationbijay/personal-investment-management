import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor()

tables = ['raw_mf_nepsealpha_assets_lastmonth', 'mf_assets_value_change']
for table in tables:
    cur.execute(f"""
        SELECT tgname, pg_get_triggerdef(oid) 
        FROM pg_trigger 
        WHERE tgrelid = '{table}'::regclass AND tgisinternal = false;
    """)
    print(f"--- Triggers for {table} ---")
    for row in cur.fetchall():
        print(row[1])

cur.close()
conn.close()
