import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

sql = """
CREATE OR REPLACE FUNCTION public.fn_calculate_mf_asset_ltps()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
        DECLARE
            v_nav_ltp REAL;
            v_actual_date DATE;
            v_today_ltp REAL;
        BEGIN
            -- 1. Get LTP and Date for the weekly nav date (Fallback to earlier if holiday)
            SELECT "LTP", "Date" INTO v_nav_ltp, v_actual_date
            FROM public.raw_price_history
            WHERE symbol = NEW.symbol
            AND "Date" <= TO_DATE(NEW."weekly nav date", 'MM/DD/YYYY')
            ORDER BY "Date" DESC
            LIMIT 1;

            -- 2. Get the most recent LTP (today's ltp)
            SELECT "LTP" INTO v_today_ltp
            FROM public.raw_price_history
            WHERE symbol = NEW.symbol
            ORDER BY "Date" DESC
            LIMIT 1;

            -- 3. Assign values
            NEW."weekly nav day ltp" := v_nav_ltp;
            NEW.weekly_nav_date_actual := v_actual_date;
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

CREATE OR REPLACE FUNCTION public.fn_update_mf_analytics_on_price_change()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
        BEGIN
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
                weekly_nav_date_actual = NEW."Date"
            WHERE symbol = NEW.symbol
            AND NEW."Date" = (
                SELECT "Date"
                FROM public.raw_price_history
                WHERE symbol = NEW.symbol
                AND "Date" <= TO_DATE("weekly nav date", 'MM/DD/YYYY')
                ORDER BY "Date" DESC
                LIMIT 1
            );

            RETURN NEW;
        END;
        $function$
;
"""

conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor()

try:
    cur.execute(sql)
    conn.commit()
    print("Successfully updated fallback date logic!")
except Exception as e:
    conn.rollback()
    print(f"Error executing updated functions: {e}")

cur.close()
conn.close()
