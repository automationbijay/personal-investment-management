import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
conn = psycopg2.connect(os.environ.get("DATABASE_URL"))
cur = conn.cursor()

cur.execute("""
    SELECT conname, contype 
    FROM pg_constraint 
    WHERE conrelid = 'raw_securities'::regclass
""")
for row in cur.fetchall():
    print(row)
    
cur.close()
conn.close()
