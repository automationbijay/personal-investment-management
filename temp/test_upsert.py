import os, psycopg2
from dotenv import load_dotenv
load_dotenv()
try:
    conn = psycopg2.connect(os.getenv('DATABASE_URL'))
    cur = conn.cursor()
    cur.execute('''INSERT INTO raw_mf_nepsealpha_assets_lastmonth ("MF", symbol, "Month", quantity) 
                   VALUES ('DUMMY', 'DUMMY', '2023-01', 10) 
                   ON CONFLICT ("MF", symbol, "Month") DO UPDATE SET quantity = EXCLUDED.quantity;''')
    print('Upsert with quoted columns successful')
except Exception as e:
    print('Error:', e)
