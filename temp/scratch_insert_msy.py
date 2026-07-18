import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
conn = psycopg2.connect(os.getenv('DATABASE_URL'))
conn.autocommit = True
cur = conn.cursor()

sql1 = """
INSERT INTO public.raw_securities (id, symbol, security_name, name, active_status)
VALUES (
    (SELECT COALESCE(MAX(id), 0) + 1 FROM public.raw_securities),
    'MSY',
    'Machhapuchchhre Shreejana Yield',
    'Machhapuchchhre Shreejana Yield',
    'A'
) ON CONFLICT (symbol) DO NOTHING;
"""

sql2 = """
INSERT INTO public.raw_mutual_funds (symbol, mutual_fund_name)
VALUES ('MSY', 'Machhapuchchhre Shreejana Yield')
ON CONFLICT (symbol) DO NOTHING;
"""

try:
    cur.execute(sql1)
    cur.execute(sql2)
    print("Successfully added MSY to raw_securities and raw_mutual_funds.")
except Exception as e:
    print(f"Error: {e}")

cur.close()
conn.close()
