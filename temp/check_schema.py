import os
import psycopg2
from dotenv import load_dotenv

def check_schema():
    load_dotenv()
    db_url = os.getenv("DATABASE_URL")
    
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()
    
    # Check tables
    cur.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name IN ('raw_price_history', 'raw_nepseapi_live_prices', 'raw_securities');
    """)
    tables = cur.fetchall()
    print("Existing tables:", tables)
    
    # Check columns of raw_price_history
    if ('raw_price_history',) in tables:
        cur.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'raw_price_history';
        """)
        columns = cur.fetchall()
        print("\nColumns in raw_price_history:")
        for col in columns:
            print(f" - {col[0]} ({col[1]})")

    cur.close()
    conn.close()

if __name__ == "__main__":
    check_schema()
