import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor()

fk_configs = [
    ("raw_meroshare_wacc", "Scrip Name", "fk_wacc_symbol"),
    ("raw_meroshare_portfolio", "Scrip", "fk_portfolio_symbol"),
    ("raw_deb_marketdepth", "Symbol", "fk_marketdepth_symbol"),
    ("fundamental_data", "symbol", "fk_fundamental_symbol"),
    ("raw_mf_assets_allocation", "Symbol", "fk_assets_alloc_symbol")
]

for table, column, fk_name in fk_configs:
    try:
        cur.execute(f"""
            ALTER TABLE public.{table}
            ADD CONSTRAINT {fk_name}
            FOREIGN KEY ("{column}") REFERENCES public.raw_securities("symbol") NOT VALID;
        """)
        print(f"Successfully added {fk_name} to {table}.")
    except Exception as e:
        print(f"Error adding {fk_name} to {table}: {e}")
        conn.rollback()
        continue
    
conn.commit()
cur.close()
conn.close()
