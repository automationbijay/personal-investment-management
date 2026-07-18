import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
db_url = os.getenv('DATABASE_URL')
conn = psycopg2.connect(db_url)
cur = conn.cursor()

def get_schema(table):
    cur.execute(f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{table}';")
    return cur.fetchall()

print('raw_mf_nepsealpha_assets_lastmonth:', get_schema('raw_mf_nepsealpha_assets_lastmonth'))
print('raw_mf_sharesansar_nav:', get_schema('raw_mf_sharesansar_nav'))
