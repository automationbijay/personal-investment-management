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
    SELECT tc.table_name, kcu.column_name, tc.constraint_type
    FROM information_schema.table_constraints tc 
    JOIN information_schema.key_column_usage kcu ON tc.constraint_name = kcu.constraint_name AND tc.table_schema = kcu.table_schema 
    WHERE tc.table_schema = 'public' AND tc.table_name LIKE '%deb%' AND tc.constraint_type = 'PRIMARY KEY';
""")
print("Primary Keys on deb tables:")
for row in cur.fetchall():
    print(row)

cur.execute("""
    SELECT symbol, instrument_type, sector_name FROM raw_securities WHERE symbol LIKE '%D83%' OR symbol LIKE '%DEB%';
""")
print("\nSample debentures from raw_securities:")
for row in cur.fetchall()[:5]:
    print(row)

cur.close()
conn.close()
