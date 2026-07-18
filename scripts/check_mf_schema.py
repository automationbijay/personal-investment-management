"""
Investigatory script used to explore the schema of existing mutual fund tables.
"""

import os
import psycopg2
from dotenv import load_dotenv

def check_mf_schema():
    load_dotenv()
    db_url = os.getenv("DATABASE_URL")
    
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()
    
    cur.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name LIKE '%mf%';
    """)
    tables = cur.fetchall()
    print("MF tables:", tables)
    
    for table in tables:
        t_name = table[0]
        cur.execute(f"""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = '{t_name}';
        """)
        columns = cur.fetchall()
        print(f"\nColumns in {t_name}:")
        for col in columns:
            print(f" - {col[0]} ({col[1]})")

    cur.close()
    conn.close()

if __name__ == "__main__":
    check_mf_schema()
