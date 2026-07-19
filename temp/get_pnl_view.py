import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
db_url = os.getenv("DATABASE_URL")
conn = psycopg2.connect(db_url)
cur = conn.cursor()

cur.execute("SELECT pg_get_viewdef('view_profit_loss_analysis', true);")
print(cur.fetchone()[0])

cur.close()
conn.close()
