import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
conn = psycopg2.connect(os.environ.get("DATABASE_URL"))
cur = conn.cursor()

cur.execute("""
    SELECT trigger_name, action_statement 
    FROM information_schema.triggers 
    WHERE event_object_table = 'analysis_config'
""")
print("TRIGGERS:")
for row in cur.fetchall():
    print(row)
    
cur.close()
conn.close()
