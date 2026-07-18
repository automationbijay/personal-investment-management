import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
db_url = os.environ.get("DATABASE_URL")
if not db_url:
    print("DATABASE_URL not found")
    exit(1)

conn = psycopg2.connect(db_url)
cur = conn.cursor()

cur.execute("""
    SELECT tc.constraint_name, tc.table_name, ccu.table_name AS foreign_table_name
    FROM information_schema.table_constraints tc 
    JOIN information_schema.constraint_column_usage ccu ON ccu.constraint_name = tc.constraint_name AND ccu.table_schema = tc.table_schema 
    WHERE tc.table_schema = 'public' AND tc.constraint_type = 'FOREIGN KEY' AND tc.table_name = 'raw_deb_nepseapi_marketdepth';
""")
for row in cur.fetchall():
    print(row)

cur.close()
conn.close()
