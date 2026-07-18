"""
Investigatory script used to list all `raw_` prefixed tables and check for the existence of an `updated_at` column.
"""

import os
import psycopg2
from dotenv import load_dotenv

def check_raw_tables():
    load_dotenv()
    db_url = os.getenv("DATABASE_URL")
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()

    cur.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name LIKE 'raw_%';
    """)
    tables = cur.fetchall()
    
    print("RAW tables and their 'updated_at' status:")
    for t in tables:
        t_name = t[0]
        cur.execute(f"""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_schema = 'public' 
            AND table_name = '{t_name}'
            AND column_name = 'updated_at';
        """)
        has_updated = bool(cur.fetchone())
        print(f"{t_name}: {'Has updated_at' if has_updated else 'MISSING updated_at'}")

    cur.close()
    conn.close()

if __name__ == "__main__":
    check_raw_tables()
