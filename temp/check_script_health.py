import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
db_url = os.getenv('DATABASE_URL')

if db_url:
    try:
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        
        print("--- sys_script_health data ---")
        cur.execute("""
            SELECT * FROM sys_script_health 
            WHERE script_name ILIKE '%meroshare%';
        """)
        columns = [desc[0] for desc in cur.description]
        print(columns)
        for row in cur.fetchall():
            print(row)
            
        print("\\n--- Triggers on raw_meroshare_portfolio ---")
        cur.execute("""
            SELECT trigger_name, action_statement 
            FROM information_schema.triggers 
            WHERE event_object_table = 'raw_meroshare_portfolio';
        """)
        for row in cur.fetchall():
            print(row)

        print("\\n--- Triggers on raw_meroshare_wacc ---")
        cur.execute("""
            SELECT trigger_name, action_statement 
            FROM information_schema.triggers 
            WHERE event_object_table = 'raw_meroshare_wacc';
        """)
        for row in cur.fetchall():
            print(row)

        cur.close()
        conn.close()
    except Exception as e:
        print('Error:', e)
