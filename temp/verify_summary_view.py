import os, psycopg2
from dotenv import load_dotenv
load_dotenv()
conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor()
cur.execute('SELECT * FROM vw_mf_summary_analytics LIMIT 5')
cols = [desc[0] for desc in cur.description]
print(cols)
for row in cur.fetchall():
    print(row)
