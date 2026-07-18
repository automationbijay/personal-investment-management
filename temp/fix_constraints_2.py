import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
db_url = os.getenv("DATABASE_URL")

conn = psycopg2.connect(db_url)
conn.autocommit = True
cur = conn.cursor()

commands = [
    # Insert GSYM if missing
    "INSERT INTO public.raw_securities (symbol, instrument_type) VALUES ('GSYM', 'Equity') ON CONFLICT (symbol) DO NOTHING;",
    # Re-add failed foreign keys
    "ALTER TABLE public.raw_meroshare_wacc ADD CONSTRAINT fk_wacc_symbol FOREIGN KEY (symbol) REFERENCES public.raw_securities(symbol) NOT VALID;",
    "ALTER TABLE public.raw_meroshare_portfolio ADD CONSTRAINT fk_portfolio_symbol FOREIGN KEY (symbol) REFERENCES public.raw_securities(symbol) NOT VALID;",
]

for cmd in commands:
    print(f"Executing: {cmd}")
    try:
        cur.execute(cmd)
    except Exception as e:
        print(f"Error: {e}")

conn.close()
