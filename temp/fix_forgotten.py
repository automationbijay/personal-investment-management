import os
import psycopg2
from dotenv import load_dotenv

def fix_forgotten():
    load_dotenv()
    db_url = os.getenv("DATABASE_URL")
    if db_url:
        print("Connecting to DB to fix missing items...")
        try:
            conn = psycopg2.connect(db_url)
            conn.autocommit = True
            cur = conn.cursor()
            
            cur.execute("DROP MATERIALIZED VIEW IF EXISTS deb_price_stats CASCADE;")
            print("Dropped materialized view deb_price_stats")
            
            cur.close()
            conn.close()
        except Exception as e:
            print(f"DB Error: {e}")

if __name__ == "__main__":
    fix_forgotten()
