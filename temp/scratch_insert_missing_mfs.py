import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor()

sql_insert = """
INSERT INTO public.raw_mutual_funds (symbol)
SELECT DISTINCT a.symbol 
FROM public.raw_mf_nepsealpha_assets_allocation a
INNER JOIN public.raw_securities s ON a.symbol = s.symbol
WHERE a.symbol IS NOT NULL
ON CONFLICT (symbol) DO NOTHING;
"""

sql_missing = """
SELECT DISTINCT a.symbol 
FROM public.raw_mf_nepsealpha_assets_allocation a
LEFT JOIN public.raw_securities s ON a.symbol = s.symbol
WHERE a.symbol IS NOT NULL AND s.symbol IS NULL;
"""

try:
    cur.execute(sql_insert)
    conn.commit()
    print("Successfully inserted valid symbols into raw_mutual_funds!")
    
    cur.execute(sql_missing)
    missing = [row[0] for row in cur.fetchall()]
    if missing:
        print(f"Skipped these symbols because they are missing from raw_securities: {missing}")
except Exception as e:
    conn.rollback()
    print(f"Error: {e}")
    
cur.close()
conn.close()
