import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
db_url = os.environ.get("DATABASE_URL")
if not db_url:
    print("DATABASE_URL not found")
    exit(1)

conn = psycopg2.connect(db_url)
cur = conn.cursor()

cur.execute("""
    SELECT indexname 
    FROM pg_indexes 
    WHERE schemaname = 'public' 
    AND indexname IN (
        'idx_raw_mf_nepsealpha_assets_lastmonth_symbol',
        'idx_raw_mf_nepsealpha_assets_lastmonth_month',
        'idx_raw_price_history_date',
        'idx_mf_assets_analytics_symbol',
        'idx_mf_assets_analytics_month',
        'idx_fundamental_data_date'
    );
""")
print("Existing target indexes:")
for row in cur.fetchall():
    print(row[0])

cur.close()
conn.close()
