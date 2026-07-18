import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
db_url = os.getenv('DATABASE_URL')

if not db_url:
    print('No DATABASE_URL found.')
    exit(1)

sql = """
ALTER TABLE raw_mutual_funds
    DROP COLUMN IF EXISTS mutual_fund_name,
    DROP COLUMN IF EXISTS fund_size,
    DROP COLUMN IF EXISTS maturity_date,
    DROP COLUMN IF EXISTS maturity_period,
    DROP COLUMN IF EXISTS source;
"""

try:
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()
    
    print("Dropping redundant columns from raw_mutual_funds...")
    cur.execute(sql)
    conn.commit()
    print("Successfully simplified table.")
    
    cur.close()
    conn.close()
except Exception as e:
    print('Error:', e)
