import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor()

sql = """
CREATE OR REPLACE FUNCTION public.fn_update_mf_analytics_on_price_change()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
        BEGIN
            -- Prevent recursive trigger loops (e.g. from fn_calculate_mf_asset_ltps)
            IF pg_trigger_depth() > 1 THEN
                RETURN NEW;
            END IF;

            -- Update today's ltp and today's nav value for all matching symbols
            UPDATE public.mf_assets_value_change
            SET "today's ltp" = NEW."LTP",
                "today's Nav Value" = quantity * NEW."LTP",
                "nav changed" = (quantity * NEW."LTP") - "weekly Nav Value",
                "nav changed in percentage" = CASE 
                    WHEN "weekly Nav Value" IS NOT NULL AND "weekly Nav Value" != 0 
                    THEN (((quantity * NEW."LTP") - "weekly Nav Value") / "weekly Nav Value") * 100 
                    ELSE NULL 
                END
            WHERE symbol = NEW.symbol;

            -- Update weekly nav day ltp if the new record is the fallback nav date
            UPDATE public.mf_assets_value_change
            SET "weekly nav day ltp" = NEW."LTP",
                "weekly Nav Value" = quantity * NEW."LTP",
                "nav changed" = "today's Nav Value" - (quantity * NEW."LTP"),
                "nav changed in percentage" = CASE 
                    WHEN (quantity * NEW."LTP") != 0 
                    THEN (("today's Nav Value" - (quantity * NEW."LTP")) / (quantity * NEW."LTP")) * 100 
                    ELSE NULL 
                END,
                weekly_nav_date_actual = TO_DATE("weekly nav date", 'MM/DD/YYYY')
            WHERE symbol = NEW.symbol
            AND NEW."Date" = TO_DATE("weekly nav date", 'MM/DD/YYYY');

            RETURN NEW;
        END;
        $function$
;
"""

try:
    cur.execute(sql)
    conn.commit()
    print("Fixed fn_update_mf_analytics_on_price_change loop with pg_trigger_depth!")
except Exception as e:
    conn.rollback()
    print(f"Error: {e}")
    
cur.close()
conn.close()
