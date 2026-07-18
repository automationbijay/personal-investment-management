import os
import psycopg2
from dotenv import load_dotenv

def drop_view():
    load_dotenv()
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("DATABASE_URL not found in .env")
        return

    try:
        conn = psycopg2.connect(db_url)
        conn.autocommit = True
        cur = conn.cursor()
        
        print("Dropping vw_live_vs_history_price...")
        cur.execute("DROP VIEW IF EXISTS vw_live_vs_history_price;")
        print("View dropped successfully.")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    drop_view()
