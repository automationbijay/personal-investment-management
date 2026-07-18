import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor()

cur.execute('SELECT "Scrip Name" FROM raw_meroshare_wacc LIMIT 5;')
print('--- WACC ---')
for row in cur.fetchall():
    print(row)

cur.execute('SELECT "Scrip" FROM raw_meroshare_portfolio LIMIT 5;')
print('--- PORTFOLIO ---')
for row in cur.fetchall():
    print(row)

cur.close()
conn.close()
