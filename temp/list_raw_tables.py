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
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name LIKE 'raw_%';
        """)
        tables = [row[0] for row in cur.fetchall()]
        print("Raw Tables:", tables)
        
        cur.close()
        conn.close()
    except Exception as e:
        print('Error:', e)
