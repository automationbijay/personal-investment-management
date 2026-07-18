import os, psycopg2
from dotenv import load_dotenv
load_dotenv()
conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor()
cur.execute('SELECT "Month" FROM raw_mf_nepsealpha_assets_lastmonth LIMIT 5')
print('ast Month:', cur.fetchall())
