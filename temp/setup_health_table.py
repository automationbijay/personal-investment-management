"""
One-off script to create the `sys_script_health` schema for tracking script execution statuses.
"""

import os
import psycopg2
from dotenv import load_dotenv

def setup_health_table():
    load_dotenv()
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("DATABASE_URL not found in .env")
        return

    conn = psycopg2.connect(db_url)
    conn.autocommit = True
    cur = conn.cursor()

    try:
        print("Creating sys_script_health table...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS sys_script_health (
                script_name TEXT PRIMARY KEY,
                last_run TIMESTAMP WITH TIME ZONE,
                health_status TEXT,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
        """)
        print("Successfully created sys_script_health table.")
        
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    setup_health_table()
