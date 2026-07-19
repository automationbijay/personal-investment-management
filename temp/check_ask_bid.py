import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
db_url = os.getenv("DATABASE_URL")
conn = psycopg2.connect(db_url)
cur = conn.cursor()

cur.execute("""
    SELECT table_name 
    FROM information_schema.views 
    WHERE table_schema = 'public' 
    AND table_name LIKE '%mf_ask_bid%';
""")
print("Views matching '%mf_ask_bid%':")
for row in cur.fetchall():
    print(row)

cur.close()
conn.close()
