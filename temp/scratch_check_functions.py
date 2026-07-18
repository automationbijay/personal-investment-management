import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor()

cur.execute("""
    SELECT proname, prosrc 
    FROM pg_proc 
    WHERE prosrc ILIKE '%"Symbol"%' OR 
          prosrc ILIKE '%"Scrip"%' OR 
          prosrc ILIKE '%"Scrip Name"%' OR
          prosrc ILIKE '%raw_live_prices%' OR
          prosrc ILIKE '%raw_deb_marketdepth%' OR
          prosrc ILIKE '%raw_mf_assets_allocation%' OR
          prosrc ILIKE '%raw_deb_nepsealpha%';
""")
print('--- FUNCTIONS TO UPDATE ---')
for name, _ in cur.fetchall():
    print(name)

cur.close()
conn.close()
