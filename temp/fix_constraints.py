import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
db_url = os.getenv("DATABASE_URL")

conn = psycopg2.connect(db_url)
conn.autocommit = True
cur = conn.cursor()

commands = [
    # 1. Drop foreign keys referencing raw_securities_symbol_key
    "ALTER TABLE public.raw_nepseapi_live_prices DROP CONSTRAINT IF EXISTS fk_live_prices_symbol;",
    "ALTER TABLE public.raw_price_history DROP CONSTRAINT IF EXISTS fk_price_history_symbol;",
    "ALTER TABLE public.raw_meroshare_wacc DROP CONSTRAINT IF EXISTS fk_wacc_symbol;",
    "ALTER TABLE public.raw_meroshare_portfolio DROP CONSTRAINT IF EXISTS fk_portfolio_symbol;",
    "ALTER TABLE public.raw_deb_nepseapi_marketdepth DROP CONSTRAINT IF EXISTS fk_marketdepth_symbol;",
    "ALTER TABLE public.fundamental_data DROP CONSTRAINT IF EXISTS fk_fundamental_symbol;",
    "ALTER TABLE public.raw_mutual_funds DROP CONSTRAINT IF EXISTS fk_mf_securities;",
    
    # 2. Drop raw_securities_symbol_key constraint
    "ALTER TABLE public.raw_securities DROP CONSTRAINT IF EXISTS raw_securities_symbol_key;",
    
    # 3. Re-add foreign keys referencing raw_securities(symbol) - which will now use the PK
    "ALTER TABLE public.raw_nepseapi_live_prices ADD CONSTRAINT fk_live_prices_symbol FOREIGN KEY (symbol) REFERENCES public.raw_securities(symbol);",
    "ALTER TABLE public.raw_price_history ADD CONSTRAINT fk_price_history_symbol FOREIGN KEY (symbol) REFERENCES public.raw_securities(symbol);",
    "ALTER TABLE public.raw_meroshare_wacc ADD CONSTRAINT fk_wacc_symbol FOREIGN KEY (symbol) REFERENCES public.raw_securities(symbol);",
    "ALTER TABLE public.raw_meroshare_portfolio ADD CONSTRAINT fk_portfolio_symbol FOREIGN KEY (symbol) REFERENCES public.raw_securities(symbol);",
    "ALTER TABLE public.raw_deb_nepseapi_marketdepth ADD CONSTRAINT fk_marketdepth_symbol FOREIGN KEY (symbol) REFERENCES public.raw_securities(symbol);",
    "ALTER TABLE public.fundamental_data ADD CONSTRAINT fk_fundamental_symbol FOREIGN KEY (symbol) REFERENCES public.raw_securities(symbol);",
    "ALTER TABLE public.raw_mutual_funds ADD CONSTRAINT fk_mf_securities FOREIGN KEY (symbol) REFERENCES public.raw_securities(symbol);",
    
    # 4. Drop foreign key referencing unique_symbol_date
    "ALTER TABLE public.mf_assets_value_change DROP CONSTRAINT IF EXISTS fk_mf_assets_price_history;",
    
    # 5. Drop unique_symbol_date constraint
    "ALTER TABLE public.raw_price_history DROP CONSTRAINT IF EXISTS unique_symbol_date;",
    
    # 6. Re-add foreign key referencing raw_price_history(symbol, "Date") - which will now use the PK
    "ALTER TABLE public.mf_assets_value_change ADD CONSTRAINT fk_mf_assets_price_history FOREIGN KEY (symbol, weekly_nav_date_actual) REFERENCES public.raw_price_history(symbol, \"Date\");"
]

for cmd in commands:
    print(f"Executing: {cmd}")
    try:
        cur.execute(cmd)
    except Exception as e:
        print(f"Error: {e}")

conn.close()
