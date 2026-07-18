import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor()

sql = """
ALTER TABLE public.raw_mf_sharesansar_nav DROP CONSTRAINT IF EXISTS fk_mf_nav_symbol;
ALTER TABLE public.raw_mf_nepsealpha_assets_allocation DROP CONSTRAINT IF EXISTS fk_assets_alloc_symbol;
"""

try:
    cur.execute(sql)
    conn.commit()
    print("Successfully dropped the old constraints pointing to raw_securities.")
except Exception as e:
    conn.rollback()
    print(f"Error: {e}")
    
cur.close()
conn.close()
