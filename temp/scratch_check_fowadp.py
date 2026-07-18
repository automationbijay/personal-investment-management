import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor()

cur.execute("SELECT COUNT(*) FROM raw_price_history WHERE symbol='FOWADP'")
print(f"FOWADP history count: {cur.fetchone()[0]}")

cur.execute("SELECT * FROM raw_price_history WHERE symbol='FOWADP'")
print(cur.fetchall())
cur.close()
conn.close()
