import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor()

sql = """
-- 1. Create raw_mutual_funds table
CREATE TABLE IF NOT EXISTS public.raw_mutual_funds (
    symbol TEXT PRIMARY KEY,
    mutual_fund_name TEXT,
    fund_size TEXT,
    maturity_date TEXT,
    maturity_period TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_mf_securities FOREIGN KEY (symbol) REFERENCES public.raw_securities(symbol) ON DELETE CASCADE
);

-- 2. Populate raw_mutual_funds from existing data in raw_mf_sharesansar_nav
INSERT INTO public.raw_mutual_funds (symbol, mutual_fund_name, fund_size, maturity_date, maturity_period)
SELECT DISTINCT 
    symbol, 
    "Mutual_Fund_Name", 
    "Fund_Size", 
    "Maturity_Date", 
    "Maturity_Period"
FROM public.raw_mf_sharesansar_nav
WHERE symbol IS NOT NULL
ON CONFLICT (symbol) DO UPDATE SET
    mutual_fund_name = EXCLUDED.mutual_fund_name,
    fund_size = EXCLUDED.fund_size,
    maturity_date = EXCLUDED.maturity_date,
    maturity_period = EXCLUDED.maturity_period;

-- 3. Modify Foreign Keys on Child Tables
-- For mf_assets_analytics
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_mf_analytics_symbol') THEN
        ALTER TABLE public.mf_assets_analytics DROP CONSTRAINT fk_mf_analytics_symbol;
    END IF;
    ALTER TABLE public.mf_assets_analytics ADD CONSTRAINT fk_mf_analytics_symbol FOREIGN KEY (symbol) REFERENCES public.raw_mutual_funds(symbol) NOT VALID;
END $$;

-- For raw_mf_nepsealpha_assets_allocation
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_mf_assets_alloc_symbol') THEN
        ALTER TABLE public.raw_mf_nepsealpha_assets_allocation DROP CONSTRAINT fk_mf_assets_alloc_symbol;
    END IF;
    ALTER TABLE public.raw_mf_nepsealpha_assets_allocation ADD CONSTRAINT fk_mf_assets_alloc_symbol FOREIGN KEY (symbol) REFERENCES public.raw_mutual_funds(symbol) NOT VALID;
END $$;

-- For raw_mf_sharesansar_nav
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_sharesansar_nav_symbol') THEN
        ALTER TABLE public.raw_mf_sharesansar_nav DROP CONSTRAINT fk_sharesansar_nav_symbol;
    END IF;
    ALTER TABLE public.raw_mf_sharesansar_nav ADD CONSTRAINT fk_sharesansar_nav_symbol FOREIGN KEY (symbol) REFERENCES public.raw_mutual_funds(symbol) NOT VALID;
END $$;

-- For raw_mf_nepsealpha_assets_lastmonth
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_mf_assets_lastmonth_mf') THEN
        ALTER TABLE public.raw_mf_nepsealpha_assets_lastmonth DROP CONSTRAINT fk_mf_assets_lastmonth_mf;
    END IF;
    ALTER TABLE public.raw_mf_nepsealpha_assets_lastmonth ADD CONSTRAINT fk_mf_assets_lastmonth_mf FOREIGN KEY ("MF") REFERENCES public.raw_mutual_funds(symbol) NOT VALID;
END $$;
"""

try:
    cur.execute(sql)
    conn.commit()
    print("Successfully created raw_mutual_funds and updated foreign keys!")
except Exception as e:
    conn.rollback()
    print(f"Error: {e}")
    
cur.close()
conn.close()
