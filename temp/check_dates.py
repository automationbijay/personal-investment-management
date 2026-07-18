import os, psycopg2
from dotenv import load_dotenv
load_dotenv()
conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor()
cur.execute('SELECT "Date" FROM raw_price_history LIMIT 5')
print('raw_price_history Dates:', cur.fetchall())
cur.execute('SELECT "Monthly_Nav_Date", "Weekly_Nav_Date" FROM raw_mf_sharesansar_nav LIMIT 5')
print('nav Dates:', cur.fetchall())
