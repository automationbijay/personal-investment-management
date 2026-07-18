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
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'raw_securities';
        """)
        print('raw_securities columns:', cur.fetchall())
        
        cur.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'raw_meroshare_portfolio';
        """)
        print('raw_meroshare_portfolio columns:', cur.fetchall())
        
        cur.close()
        conn.close()
    except Exception as e:
        print('Error:', e)
else:
    print('No DATABASE_URL found.')
