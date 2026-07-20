import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
conn = psycopg2.connect(os.environ['DATABASE_URL'])
conn.autocommit = True
cur = conn.cursor()

print("Dropping trigger 'analytics_sync' on 'raw_meroshare_portfolio'...")
cur.execute("DROP TRIGGER IF EXISTS analytics_sync ON raw_meroshare_portfolio;")
print("Trigger dropped successfully.")

print("Dropping function 'refresh_on_portfolio_update'...")
cur.execute("DROP FUNCTION IF EXISTS refresh_on_portfolio_update CASCADE;")
print("Function dropped successfully.")

conn.close()
print("Done.")
