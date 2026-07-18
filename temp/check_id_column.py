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
            SELECT column_default, is_identity, identity_generation
            FROM information_schema.columns 
            WHERE table_name = 'raw_securities' AND column_name = 'id';
        """)
        print('id column info:', cur.fetchall())
        
        cur.close()
        conn.close()
    except Exception as e:
        print('Error:', e)
