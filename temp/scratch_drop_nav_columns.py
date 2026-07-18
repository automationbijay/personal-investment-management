import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor()

try:
    cur.execute("BEGIN;")
    # Attempt to drop columns
    cur.execute("""
        ALTER TABLE public.raw_mf_sharesansar_nav 
        DROP COLUMN IF EXISTS "Mutual_Fund_Name",
        DROP COLUMN IF EXISTS "Maturity_Date",
        DROP COLUMN IF EXISTS "Maturity_Period",
        DROP COLUMN IF EXISTS "Fund_Size";
    """)
    conn.commit()
    print("Successfully dropped redundant columns from raw_mf_sharesansar_nav.")
except Exception as e:
    conn.rollback()
    print(f"Error dropping columns (could be dependencies): {e}")

cur.close()
conn.close()
