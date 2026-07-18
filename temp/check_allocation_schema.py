import os, psycopg2
from dotenv import load_dotenv
load_dotenv()
conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor()
cur.execute('SELECT * FROM raw_mf_nepsealpha_assets_allocation LIMIT 1')
cols = [desc[0] for desc in cur.description]
print('Cols:', cols)
