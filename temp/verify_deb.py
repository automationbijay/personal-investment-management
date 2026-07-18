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

# 1. Check raw_debentures
cur.execute("SELECT COUNT(*) FROM public.raw_debentures;")
count = cur.fetchone()[0]
print(f"raw_debentures has {count} rows.")

# 2. Check foreign keys
cur.execute("""
    SELECT tc.table_name, kcu.column_name, ccu.table_name AS foreign_table_name, ccu.column_name AS foreign_column_name 
    FROM information_schema.table_constraints tc 
    JOIN information_schema.key_column_usage kcu ON tc.constraint_name = kcu.constraint_name AND tc.table_schema = kcu.table_schema 
    JOIN information_schema.constraint_column_usage ccu ON ccu.constraint_name = tc.constraint_name AND ccu.table_schema = tc.table_schema 
    WHERE tc.table_schema = 'public' AND tc.constraint_type = 'FOREIGN KEY' AND tc.table_name LIKE '%deb%';
""")
fks = cur.fetchall()
print("\nForeign keys on debenture tables:")
for fk in fks:
    print(fk)

# 3. Check RLS
cur.execute("""
    SELECT relname, relrowsecurity 
    FROM pg_class 
    WHERE relname = 'raw_debentures';
""")
rls = cur.fetchone()
print(f"\nRLS on raw_debentures enabled: {rls[1]}")

cur.close()
conn.close()
