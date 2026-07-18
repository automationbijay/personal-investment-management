import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor()

sql = """
CREATE OR REPLACE FUNCTION public.fn_sync_analytics_from_raw()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
        BEGIN
            IF (TG_OP = 'INSERT') THEN
                -- Insert using the new composite primary key ON CONFLICT
                INSERT INTO public.mf_assets_value_change (
                    "MF", symbol, "Month", quantity
                )
                VALUES (
                    NEW."MF", NEW.symbol, NEW."Month", NEW.quantity
                )
                ON CONFLICT ("MF", symbol) DO UPDATE SET
                    "Month" = EXCLUDED."Month",
                    quantity = EXCLUDED.quantity;
                
                -- Also fetch nav date after insert (matching on MF and symbol instead of Pkey)
                UPDATE public.mf_assets_value_change m
                SET "weekly nav date" = s."Weekly_Nav_Date"
                FROM public.raw_mf_sharesansar_nav s
                WHERE m."MF" = s.symbol
                AND m."MF" = NEW."MF"
                AND m.symbol = NEW.symbol;
                
            ELSIF (TG_OP = 'DELETE') THEN
                -- Delete matching on MF and symbol instead of Pkey
                DELETE FROM public.mf_assets_value_change 
                WHERE "MF" = OLD."MF" 
                AND symbol = OLD.symbol;
            END IF;
            RETURN NULL;
        END;
        $function$
;
"""

try:
    cur.execute(sql)
    conn.commit()
    print("Successfully updated fn_sync_analytics_from_raw to use composite keys!")
except Exception as e:
    conn.rollback()
    print(f"Error: {e}")
    
cur.close()
conn.close()
