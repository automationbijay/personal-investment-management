import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
conn = psycopg2.connect(os.environ['DATABASE_URL'])
cur = conn.cursor()

# Get triggers for raw_meroshare_portfolio
cur.execute("""
SELECT trigger_name, event_manipulation, event_object_table, action_statement
FROM information_schema.triggers
WHERE event_object_table = 'raw_meroshare_portfolio';
""")
for row in cur.fetchall():
    print(row)
