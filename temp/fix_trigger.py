import os, psycopg2
from dotenv import load_dotenv

load_dotenv()
try:
    conn = psycopg2.connect(os.getenv('DATABASE_URL'))
    conn.autocommit = True
    cur = conn.cursor()
    
    cur.execute("""
    CREATE OR REPLACE FUNCTION public.fn_auto_create_missing_fks()
     RETURNS trigger
     LANGUAGE plpgsql
    AS $function$
    BEGIN
        -- Check if MF is missing from raw_mutual_funds
        IF NOT EXISTS (SELECT 1 FROM public.raw_mutual_funds WHERE symbol = NEW."MF") THEN
            -- raw_mutual_funds only has symbol, created_at, updated_at
            INSERT INTO public.raw_mutual_funds (symbol)
            VALUES (NEW."MF")
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
    """)
    print("Successfully updated fn_auto_create_missing_fks")
except Exception as e:
    print("Error:", e)
