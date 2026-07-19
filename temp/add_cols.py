import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
db_url = os.getenv("DATABASE_URL")
conn = psycopg2.connect(db_url)
conn.autocommit = True
cur = conn.cursor()

alter_sql = """
ALTER TABLE raw_mf_sharesansar_nav
ADD COLUMN IF NOT EXISTS "Fund_Size" numeric,
ADD COLUMN IF NOT EXISTS "Mutual_Fund_Name" text,
ADD COLUMN IF NOT EXISTS "Maturity_Date" text,
ADD COLUMN IF NOT EXISTS "Maturity_Period" text;
"""
cur.execute(alter_sql)
print("Columns added.")

cur.close()
conn.close()
