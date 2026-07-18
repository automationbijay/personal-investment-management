import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor()

cur.execute("""
    SELECT table_name, column_name 
    FROM information_schema.columns 
    WHERE table_schema = 'public'
    ORDER BY table_name, ordinal_position;
""")
tables = {}
for t, c in cur.fetchall():
    if t not in tables:
        tables[t] = []
    tables[t].append(c)

print('--- ALL TABLES AND COLUMNS ---')
for t, cols in tables.items():
    print(f"Table: {t}")
    print(f"Columns: {cols}")

cur.close()
conn.close()
