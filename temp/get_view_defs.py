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
    SELECT viewname, definition 
    FROM pg_views 
    WHERE schemaname = 'public' 
    AND viewname IN ('mf_assets_value_change', 'vw_mf_summary_analytics');
""")

with open("temp/view_defs.txt", "w", encoding="utf-8") as f:
    for row in cur.fetchall():
        f.write(f"--- {row[0]} ---\n{row[1]}\n\n")

print("View definitions dumped to temp/view_defs.txt")
cur.close()
conn.close()
