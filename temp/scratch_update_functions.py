import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

with open('backup_functions.sql', 'r', encoding='utf-8') as f:
    sql = f.read()

# Replace column names
sql = sql.replace('"Symbol"', 'symbol')
sql = sql.replace('"Scrip"', 'symbol')
sql = sql.replace('"Scrip Name"', 'symbol')

# Replace table names
sql = sql.replace('raw_deb_nepsealpha', 'raw_deb_nepsealpha_details')
sql = sql.replace('raw_mf_assets_allocation', 'raw_mf_nepsealpha_assets_allocation')
sql = sql.replace('raw_deb_marketdepth', 'raw_deb_nepseapi_marketdepth')
sql = sql.replace('raw_live_prices', 'raw_nepseapi_live_prices')

with open('updated_functions.sql', 'w', encoding='utf-8') as f:
    f.write(sql)

conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor()

try:
    cur.execute(sql)
    conn.commit()
    print("Successfully updated database functions!")
except Exception as e:
    conn.rollback()
    print(f"Error executing updated functions: {e}")

cur.close()
conn.close()
