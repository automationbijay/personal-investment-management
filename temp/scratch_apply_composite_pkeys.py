import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor()

sql = """
-- 1. raw_price_history
ALTER TABLE public.raw_price_history DROP CONSTRAINT IF EXISTS raw_price_history_pkey CASCADE;
ALTER TABLE public.raw_price_history DROP COLUMN IF EXISTS "symbol-with-date";

DO $$ BEGIN
    -- Check if it already has a primary key or not, just in case CASCADE didn't catch a different name
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conrelid = 'public.raw_price_history'::regclass AND contype = 'p'
    ) THEN
        ALTER TABLE public.raw_price_history ADD PRIMARY KEY (symbol, "Date");
    END IF;
END $$;

-- 2. raw_mf_nepsealpha_assets_lastmonth
ALTER TABLE public.raw_mf_nepsealpha_assets_lastmonth DROP CONSTRAINT IF EXISTS raw_mf_nepsealpha_assets_lastmonth_pkey CASCADE;
ALTER TABLE public.raw_mf_nepsealpha_assets_lastmonth DROP COLUMN IF EXISTS "Pkey";

DO $$ BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conrelid = 'public.raw_mf_nepsealpha_assets_lastmonth'::regclass AND contype = 'p'
    ) THEN
        ALTER TABLE public.raw_mf_nepsealpha_assets_lastmonth ADD PRIMARY KEY ("MF", "symbol", "Month");
    END IF;
END $$;

-- 3. mf_assets_value_change
ALTER TABLE public.mf_assets_value_change DROP CONSTRAINT IF EXISTS mf_assets_value_change_pkey CASCADE;
ALTER TABLE public.mf_assets_value_change DROP COLUMN IF EXISTS "Pkey";

DO $$ BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conrelid = 'public.mf_assets_value_change'::regclass AND contype = 'p'
    ) THEN
        ALTER TABLE public.mf_assets_value_change ADD PRIMARY KEY ("MF", "symbol");
    END IF;
END $$;
"""

try:
    cur.execute(sql)
    conn.commit()
    print("Successfully upgraded to Composite Primary Keys!")
except Exception as e:
    conn.rollback()
    print(f"Error: {e}")
    
cur.close()
conn.close()
