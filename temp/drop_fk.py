import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
db_url = os.environ.get("DATABASE_URL")
if not db_url:
    print("DATABASE_URL not found")
    exit(1)

conn = psycopg2.connect(db_url)
conn.autocommit = True
cur = conn.cursor()

cur.execute("ALTER TABLE public.raw_deb_nepseapi_marketdepth DROP CONSTRAINT IF EXISTS fk_marketdepth_symbol CASCADE;")
print("Dropped fk_marketdepth_symbol successfully.")

cur.close()
conn.close()
