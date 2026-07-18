import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
conn = psycopg2.connect(os.getenv('DATABASE_URL'))
conn.autocommit = True
cur = conn.cursor()

alter_sql = """
ALTER TABLE public.raw_securities
ADD COLUMN IF NOT EXISTS company_email TEXT,
ADD COLUMN IF NOT EXISTS website TEXT,
ADD COLUMN IF NOT EXISTS sector_name TEXT,
ADD COLUMN IF NOT EXISTS regulatory_body TEXT,
ADD COLUMN IF NOT EXISTS instrument_type TEXT;
"""
try:
    cur.execute(alter_sql)
    print("Successfully added new columns to raw_securities.")
except Exception as e:
    print(f"Error altering table: {e}")

cur.close()
conn.close()
