import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor()

symbols = ['CSBY', 'GSYA', 'KSLY', 'MSIP', 'NADDF', 'NFCF', 'NI31', 'NIBLSF', 'NICAELIS', 'NMBSBF', 'PSIS', 'SFF', 'SLK', 'SSIS']

cur.execute("SELECT COALESCE(MAX(id), 0) FROM public.raw_securities")
max_id = cur.fetchone()[0]

sql_insert_securities = """
INSERT INTO public.raw_securities (id, symbol, security_name, name, active_status)
VALUES (%s, %s, %s, %s, 'A')
ON CONFLICT (symbol) DO NOTHING;
"""

sql_insert_mfs = """
INSERT INTO public.raw_mutual_funds (symbol)
VALUES (%s)
ON CONFLICT (symbol) DO NOTHING;
"""

try:
    current_id = max_id + 1
    for sym in symbols:
        # Use symbol as temporary name
        cur.execute(sql_insert_securities, (current_id, sym, f"{sym} Mutual Fund", f"{sym} Mutual Fund"))
        if cur.rowcount > 0:
            current_id += 1
            
        cur.execute(sql_insert_mfs, (sym,))
        
    conn.commit()
    print("Successfully added missing symbols to raw_securities and raw_mutual_funds!")
except Exception as e:
    conn.rollback()
    print(f"Error: {e}")
    
cur.close()
conn.close()
