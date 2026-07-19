import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
conn = psycopg2.connect(os.environ.get("DATABASE_URL"))
cur = conn.cursor()

cur.execute("""
    SELECT routine_definition 
    FROM information_schema.routines 
    WHERE routine_name = 'refresh_urls_on_config_update'
""")
for row in cur.fetchall():
    print(row[0])
    
cur.close()
conn.close()
