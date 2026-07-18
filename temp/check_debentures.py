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
    SELECT column_name, data_type, column_default, is_nullable
    FROM information_schema.columns
    WHERE table_name = 'raw_mutual_funds';
""")
print("raw_mutual_funds schema:")
for row in cur.fetchall():
    print(row)

cur.execute("""
    SELECT table_name
    FROM information_schema.tables
    WHERE table_name LIKE '%deb%' AND table_schema = 'public';
""")
print("\nDebenture related tables/views:")
for row in cur.fetchall():
    print(row)

cur.execute("""
    SELECT tc.table_name, kcu.column_name, ccu.table_name AS foreign_table_name, ccu.column_name AS foreign_column_name 
    FROM information_schema.table_constraints tc 
    JOIN information_schema.key_column_usage kcu ON tc.constraint_name = kcu.constraint_name AND tc.table_schema = kcu.table_schema 
    JOIN information_schema.constraint_column_usage ccu ON ccu.constraint_name = tc.constraint_name AND ccu.table_schema = tc.table_schema 
    WHERE tc.table_schema = 'public' AND tc.constraint_type = 'FOREIGN KEY' AND tc.table_name LIKE '%deb%';
""")
print("\nForeign keys on debenture tables:")
for row in cur.fetchall():
    print(row)

cur.close()
conn.close()
