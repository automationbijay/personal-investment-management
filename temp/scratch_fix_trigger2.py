import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor()

sql = """
CREATE OR REPLACE FUNCTION public.fn_calculate_mf_asset_ltps()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
        DECLARE
            v_nav_ltp REAL;
            v_actual_date DATE;
            v_today_ltp REAL;
            v_nav_date DATE;
        BEGIN
            -- If the NAV date hasn't been synced yet, skip calculations!
            IF NEW."weekly nav date" IS NULL THEN
                RETURN NEW;
            END IF;

            v_nav_date := TO_DATE(NEW."weekly nav date", 'MM/DD/YYYY');
            
            -- 1. Get LTP and Date for the weekly nav date
            SELECT "LTP", "Date" INTO v_nav_ltp, v_actual_date
            FROM public.raw_price_history
            WHERE symbol = NEW.symbol
            AND "Date" <= v_nav_date
            ORDER BY "Date" DESC
            LIMIT 1;

            -- 2. Get the most recent LTP (today's ltp)
            SELECT "LTP" INTO v_today_ltp
            FROM public.raw_price_history
            WHERE symbol = NEW.symbol
            ORDER BY "Date" DESC
            LIMIT 1;

            -- 1.5 Auto-Insert Missing Row (Option 3)
            IF v_actual_date IS NOT NULL AND v_actual_date < v_nav_date THEN
                INSERT INTO public.raw_price_history (
                    symbol, "Date", "LTP", "Open", "High", "Low", "Close", "Volume"
                ) 
                VALUES (
                    NEW.symbol, v_nav_date, v_nav_ltp, v_nav_ltp, v_nav_ltp, v_nav_ltp, v_nav_ltp, 0
                ) ON CONFLICT (symbol, "Date") DO NOTHING;
            ELSIF v_actual_date IS NULL THEN
                -- Edge Case: Stock has NO price history before the NAV date!
                v_nav_ltp := COALESCE(v_today_ltp, 0);
                INSERT INTO public.raw_price_history (
                    symbol, "Date", "LTP", "Open", "High", "Low", "Close", "Volume"
                ) 
                VALUES (
                    NEW.symbol, v_nav_date, v_nav_ltp, v_nav_ltp, v_nav_ltp, v_nav_ltp, v_nav_ltp, 0
                ) ON CONFLICT (symbol, "Date") DO NOTHING;
            END IF;

            -- 3. Assign values
            NEW."weekly nav day ltp" := v_nav_ltp;
            NEW.weekly_nav_date_actual := v_nav_date;
            NEW."today's ltp" := v_today_ltp;
            
            -- Weekly NAV Value
            IF (v_nav_ltp IS NOT NULL AND NEW.quantity IS NOT NULL) THEN
                NEW."weekly Nav Value" := NEW.quantity * v_nav_ltp;
            ELSE
                NEW."weekly Nav Value" := NULL;
            END IF;

            -- Today's NAV Value
            IF (v_today_ltp IS NOT NULL AND NEW.quantity IS NOT NULL) THEN
                NEW."today's Nav Value" := NEW.quantity * v_today_ltp;
            ELSE
                NEW."today's Nav Value" := NULL;
            END IF;

            -- Calculate Changes
            IF (NEW."today's Nav Value" IS NOT NULL AND NEW."weekly Nav Value" IS NOT NULL) THEN
                NEW."nav changed" := NEW."today's Nav Value" - NEW."weekly Nav Value";
                IF (NEW."weekly Nav Value" != 0) THEN
                    NEW."nav changed in percentage" := (NEW."nav changed" / NEW."weekly Nav Value") * 100;
                ELSE
                    NEW."nav changed in percentage" := NULL;
                END IF;
            ELSE
                NEW."nav changed" := NULL;
                NEW."nav changed in percentage" := NULL;
            END IF;

            RETURN NEW;
        END;
        $function$
;
"""

try:
    cur.execute(sql)
    conn.commit()
    print("Fixed fn_calculate_mf_asset_ltps trigger to remove symbol-with-date column!")
except Exception as e:
    conn.rollback()
    print(f"Error: {e}")
    
cur.close()
conn.close()
