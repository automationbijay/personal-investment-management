import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
db_url = os.getenv("DATABASE_URL")
conn = psycopg2.connect(db_url)
cur = conn.cursor()

query = """
SELECT event_object_table AS table_name,
       trigger_name,
       action_statement AS trigger_logic
FROM information_schema.triggers
WHERE trigger_schema = 'public'
ORDER BY trigger_name, event_object_table;
"""
cur.execute(query)
rows = cur.fetchall()

print("Current Triggers:")
for r in rows:
    print(f"Table: {r[0]} | Trigger: {r[1]}")

cur.close()
conn.close()
