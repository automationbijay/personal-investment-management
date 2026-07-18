import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
db_url = os.getenv('DATABASE_URL')

if db_url:
    try:
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        
        cur.execute("SELECT symbol, expected_dividend_pct FROM raw_mf_nepsealpha_dividends LIMIT 5;")
        print(cur.fetchall())
        
        cur.close()
        conn.close()
    except Exception as e:
        print('Error:', e)
