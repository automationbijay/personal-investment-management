import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
db_url = os.getenv("DATABASE_URL")
conn = psycopg2.connect(db_url)
cur = conn.cursor()

try:
    cur.execute("DROP VIEW IF EXISTS public.view_profit_loss_analysis CASCADE;")
    conn.commit()
    print("Old view dropped successfully.")
except Exception as e:
    print(f"FAILED: {e}")
finally:
    cur.close()
    conn.close()
