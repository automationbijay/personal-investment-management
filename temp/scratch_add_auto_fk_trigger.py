import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor()

sql = """
-- 1. Add 'source' column
ALTER TABLE public.raw_securities ADD COLUMN IF NOT EXISTS source TEXT;
ALTER TABLE public.raw_mutual_funds ADD COLUMN IF NOT EXISTS source TEXT;

-- 2. Create Trigger Function
CREATE OR REPLACE FUNCTION public.fn_auto_create_missing_fks()
RETURNS trigger
LANGUAGE plpgsql
AS $function$
BEGIN
    -- Check if MF is missing from raw_mutual_funds
    IF NOT EXISTS (SELECT 1 FROM public.raw_mutual_funds WHERE symbol = NEW."MF") THEN
        INSERT INTO public.raw_mutual_funds (symbol, mutual_fund_name, source)
        VALUES (NEW."MF", NEW."MF" || ' (Auto-added)', 'auto-placeholder-nepsealpha')
        ON CONFLICT (symbol) DO NOTHING;
    END IF;

    -- Check if symbol is missing from raw_securities
    IF NOT EXISTS (SELECT 1 FROM public.raw_securities WHERE symbol = NEW.symbol) THEN
        INSERT INTO public.raw_securities (id, symbol, security_name, name, active_status, source)
        VALUES (
            (SELECT COALESCE(MAX(id), 0) + 1 FROM public.raw_securities),
            NEW.symbol,
            NEW.symbol || ' (Auto-added)',
            NEW.symbol || ' (Auto-added)',
            'A',
            'auto-placeholder-nepsealpha'
        ) ON CONFLICT (symbol) DO NOTHING;
    END IF;

    RETURN NEW;
END;
$function$;

-- 3. Attach Trigger
DROP TRIGGER IF EXISTS trg_auto_create_missing_fks ON public.raw_mf_nepsealpha_assets_lastmonth;

CREATE TRIGGER trg_auto_create_missing_fks
BEFORE INSERT OR UPDATE ON public.raw_mf_nepsealpha_assets_lastmonth
FOR EACH ROW EXECUTE FUNCTION public.fn_auto_create_missing_fks();
"""

try:
    cur.execute(sql)
    conn.commit()
    print("Successfully added source columns and created auto-placeholder trigger!")
except Exception as e:
    conn.rollback()
    print(f"Error: {e}")

cur.close()
conn.close()
