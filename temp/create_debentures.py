import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
db_url = os.environ.get("DATABASE_URL")
if not db_url:
    print("DATABASE_URL not found")
    exit(1)

conn = psycopg2.connect(db_url)
conn.autocommit = True
cur = conn.cursor()

commands = [
    # 1. Create table
    """
    CREATE TABLE IF NOT EXISTS public.raw_debentures (
        symbol text NOT NULL,
        created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
        updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
        CONSTRAINT raw_debentures_pkey PRIMARY KEY (symbol),
        CONSTRAINT raw_debentures_symbol_fkey FOREIGN KEY (symbol) REFERENCES public.raw_securities (symbol)
    );
    """,
    # 2. Enable RLS
    "ALTER TABLE public.raw_debentures ENABLE ROW LEVEL SECURITY;",
    # 3. Backfill data
    """
    INSERT INTO public.raw_debentures (symbol)
    SELECT DISTINCT symbol FROM public.raw_securities WHERE instrument_type IN ('Corporate Debenture', 'Non-Convertible Debentures')
    ON CONFLICT (symbol) DO NOTHING;
    """,
    """
    INSERT INTO public.raw_debentures (symbol)
    SELECT DISTINCT symbol FROM public.raw_deb_nepsealpha_details
    ON CONFLICT (symbol) DO NOTHING;
    """,
    """
    INSERT INTO public.raw_debentures (symbol)
    SELECT DISTINCT symbol FROM public.raw_deb_nepseapi_marketdepth
    ON CONFLICT (symbol) DO NOTHING;
    """,
    # 4. Drop old FKs
    "ALTER TABLE public.raw_deb_nepseapi_marketdepth DROP CONSTRAINT IF EXISTS raw_deb_nepseapi_marketdepth_symbol_fkey CASCADE;",
    # 5. Add new FKs
    """
    ALTER TABLE public.raw_deb_nepseapi_marketdepth 
    ADD CONSTRAINT raw_deb_nepseapi_marketdepth_symbol_fkey 
    FOREIGN KEY (symbol) REFERENCES public.raw_debentures (symbol) ON DELETE CASCADE;
    """,
    """
    ALTER TABLE public.raw_deb_nepsealpha_details 
    ADD CONSTRAINT raw_deb_nepsealpha_details_symbol_fkey 
    FOREIGN KEY (symbol) REFERENCES public.raw_debentures (symbol) ON DELETE CASCADE;
    """
]

for cmd in commands:
    print(f"Executing: {cmd.strip()[:100]}...")
    try:
        cur.execute(cmd)
    except Exception as e:
        print(f"Error executing command: {e}")

print("Migration completed successfully.")
cur.close()
conn.close()
