import os, psycopg2, json  
from dotenv import load_dotenv  
load_dotenv()  
conn = psycopg2.connect(os.getenv('DATABASE_URL'))  
cur = conn.cursor()  
cur.execute('SELECT column_name, data_type FROM information_schema.columns WHERE table_name = \'raw_nepseapi_live_prices\';')  
print(json.dumps(cur.fetchall(), indent=2))  
