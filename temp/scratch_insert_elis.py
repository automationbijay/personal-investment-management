import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
conn = psycopg2.connect(os.getenv('DATABASE_URL'))
conn.autocommit = True
cur = conn.cursor()

sql = """
INSERT INTO public.raw_securities (id, symbol, security_name, name, active_status)
VALUES (
    (SELECT COALESCE(MAX(id), 0) + 1 FROM public.raw_securities),
    'ELIS',
    'Everest Large Investment Scheme',
    'Everest Large Investment Scheme',
    'A'
) ON CONFLICT (symbol) DO NOTHING;
"""
try:
    cur.execute(sql)
    print("Successfully added ELIS to raw_securities.")
except Exception as e:
    print(f"Error: {e}")

cur.close()
conn.close()
