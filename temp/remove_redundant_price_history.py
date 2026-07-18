"""
Cleanup script that deletes records from `raw_price_history` that are older than 60 days to keep the database lean.
"""

import os
import psycopg2
from dotenv import load_dotenv
from health_logger import log_health

def remove_redundant_price_history():
    load_dotenv()
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("DATABASE_URL not found in .env")
        return

    conn = psycopg2.connect(db_url)
    conn.autocommit = True
    cur = conn.cursor()

    try:
        print("Deleting redundant price history older than 60 days...")
        # Use DELETE query to remove records where Date is older than 60 days
        cur.execute("""
            DELETE FROM raw_price_history 
            WHERE "Date" < CURRENT_DATE - INTERVAL '60 days';
        """)
        
        # cur.rowcount returns the number of rows affected
        deleted_rows = cur.rowcount
        print(f"Successfully deleted {deleted_rows} old price records.")
        
        # Log success to health table
        log_health(
            cur=cur, 
            table_name='raw_price_history', 
            status=f'SUCCESS: Deleted {deleted_rows} records', 
            script_ran_from='local'
        )

    except Exception as e:
        print(f"An error occurred: {e}")
        log_health(
            cur=cur, 
            table_name='raw_price_history', 
            status=f'FAILED: {e}', 
            script_ran_from='local'
        )
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    remove_redundant_price_history()
