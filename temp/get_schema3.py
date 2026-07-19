import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(os.environ.get("DATABASE_URL"))
cur = conn.cursor()

# Get schema of vw_profit_loss_analysis
cur.execute("""
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_name = 'vw_profit_loss_analysis';
""")
columns = cur.fetchall()
print("\n--- SCHEMA of vw_profit_loss_analysis ---")
for col in columns:
    print(col)

cur.close()
conn.close()
