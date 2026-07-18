import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor()

tables = [
    'raw_mf_sharesansar_nav',
    'raw_mf_nepsealpha_assets_allocation',
    'raw_mf_nepsealpha_assets_lastmonth',
    'mf_assets_analytics'
]

for table in tables:
    cur.execute(f"""
        SELECT conname, pg_get_constraintdef(c.oid)
        FROM pg_constraint c
        JOIN pg_class t ON c.conrelid = t.oid
        WHERE t.relname = '{table}' AND c.contype = 'f';
    """)
    print(f"--- {table} ---")
    for row in cur.fetchall():
        print(row)

cur.close()
conn.close()
