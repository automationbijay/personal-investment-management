import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor()

cur.execute("SELECT column_name FROM information_schema.columns WHERE table_schema='public' AND table_name='raw_securities'")
print("raw_securities cols:", [r[0] for r in cur.fetchall()])

cur.execute("SELECT column_name FROM information_schema.columns WHERE table_schema='public' AND table_name='raw_mf_sharesansar_nav'")
print("raw_mf_sharesansar_nav cols:", [r[0] for r in cur.fetchall()])

cur.close()
conn.close()
