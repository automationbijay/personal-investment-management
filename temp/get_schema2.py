import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(os.environ.get("DATABASE_URL"))
cur = conn.cursor()

# Get the definition of mf_ask_bid
cur.execute("SELECT pg_get_viewdef('mf_ask_bid', true);")
view_def = cur.fetchone()[0]
print("--- VIEW DEFINITION for mf_ask_bid ---")
print(view_def)

# Get schema of raw_meroshare_wacc
cur.execute("""
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_name = 'raw_meroshare_wacc';
""")
columns = cur.fetchall()
print("\n--- SCHEMA of raw_meroshare_wacc ---")
for col in columns:
    print(col)

cur.close()
conn.close()
