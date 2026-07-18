import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor()

cur.execute("SELECT pg_get_functiondef(oid) FROM pg_proc WHERE proname = 'fn_sync_analytics_from_raw'")
print(cur.fetchone()[0])
cur.close()
conn.close()
