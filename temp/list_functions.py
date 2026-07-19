import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
db_url = os.getenv("DATABASE_URL")
conn = psycopg2.connect(db_url)
cur = conn.cursor()

query = """
SELECT routine_name 
FROM information_schema.routines 
WHERE routine_type='FUNCTION' AND specific_schema='public';
"""
cur.execute(query)
for r in cur.fetchall():
    print(r[0])

cur.close()
conn.close()
