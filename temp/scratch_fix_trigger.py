import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

sql = """
CREATE OR REPLACE FUNCTION public.fn_sync_analytics_from_raw()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
        BEGIN
            IF (TG_OP = 'INSERT') THEN
                INSERT INTO public.mf_assets_value_change (
                    "MF", symbol, "Month", quantity, "Pkey"
                )
                VALUES (
                    NEW."MF", NEW.symbol, NEW."Month", NEW.quantity, NEW."Pkey"
                )
                ON CONFLICT ("Pkey") DO UPDATE SET
                    "MF" = EXCLUDED."MF",
                    symbol = EXCLUDED.symbol,
                    "Month" = EXCLUDED."Month",
                    quantity = EXCLUDED.quantity;
                
                -- Also fetch nav date after insert
                UPDATE public.mf_assets_value_change m
                SET "weekly nav date" = s."Weekly_Nav_Date"
                FROM public.raw_mf_sharesansar_nav s
                WHERE m."MF" = s.symbol
                AND m."Pkey" = NEW."Pkey";
                
            ELSIF (TG_OP = 'DELETE') THEN
                DELETE FROM public.mf_assets_value_change WHERE "Pkey" = OLD."Pkey";
            END IF;
            RETURN NULL;
        END;
        $function$
;
"""

conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor()

try:
    cur.execute(sql)
    conn.commit()
    print("Successfully fixed fn_sync_analytics_from_raw!")
except Exception as e:
    conn.rollback()
    print(f"Error executing updated functions: {e}")

cur.close()
conn.close()
