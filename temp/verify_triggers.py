import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
db_url = os.getenv('DATABASE_URL')

if db_url:
    try:
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        
        cur.execute("""
            SELECT event_object_table, trigger_name, event_manipulation 
            FROM information_schema.triggers 
            WHERE trigger_name = 'trg_auto_health'
            ORDER BY event_object_table;
        """)
        for row in cur.fetchall():
            print(row)
        
        cur.close()
        conn.close()
    except Exception as e:
        print('Error:', e)
