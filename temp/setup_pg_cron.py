import os
import psycopg2
from dotenv import load_dotenv

def setup_pg_cron():
    load_dotenv()
    db_url = os.getenv("DATABASE_URL")
    conn = psycopg2.connect(db_url)
    conn.autocommit = True
    cur = conn.cursor()

    sql = """
    -- 1. Ensure pg_cron is enabled
    CREATE EXTENSION IF NOT EXISTS pg_cron WITH SCHEMA extensions;

    -- 2. Create the Averages Function
    CREATE OR REPLACE FUNCTION public.fn_cron_populate_averages()
    RETURNS void
    LANGUAGE plpgsql
    AS $function$
    BEGIN
        WITH ranked_history AS (
            SELECT 
                symbol,
                "Date",
                "LTP",
                "Volume",
                "VWAP",
                ROW_NUMBER() OVER (PARTITION BY symbol ORDER BY "Date" DESC) as rn
            FROM public.raw_price_history
            WHERE "LTP" IS NOT NULL
        ),
        averages AS (
            SELECT
                symbol,
                MAX("Date") as last_date,
                ROUND(AVG("LTP") FILTER (WHERE rn <= 5), 2) as ltp_avg_5d,
                ROUND(AVG("LTP") FILTER (WHERE rn <= 10), 2) as ltp_avg_10d,
                ROUND(AVG("LTP") FILTER (WHERE rn <= 30), 2) as ltp_avg_30d,
                ROUND(AVG("LTP"), 2) as ltp_avg_all,
                ROUND(AVG("Volume") FILTER (WHERE rn <= 5), 2) as volume_avg_5d,
                ROUND(AVG("Volume") FILTER (WHERE rn <= 10), 2) as volume_avg_10d,
                ROUND(AVG("Volume") FILTER (WHERE rn <= 30), 2) as volume_avg_30d,
                ROUND(AVG("Volume"), 2) as volume_avg_all,
                ROUND(AVG("VWAP") FILTER (WHERE rn <= 5), 2) as vwap_avg_5d,
                ROUND(AVG("VWAP") FILTER (WHERE rn <= 10), 2) as vwap_avg_10d,
                ROUND(AVG("VWAP") FILTER (WHERE rn <= 30), 2) as vwap_avg_30d,
                ROUND(AVG("VWAP"), 2) as vwap_avg_all
            FROM ranked_history
            GROUP BY symbol
        )
        INSERT INTO public.wiki_average (
            symbol, "Date",
            ltp_avg_5d, ltp_avg_10d, ltp_avg_30d, ltp_avg_all,
            volume_avg_5d, volume_avg_10d, volume_avg_30d, volume_avg_all,
            vwap_avg_5d, vwap_avg_10d, vwap_avg_30d, vwap_avg_all,
            updated_at
        )
        SELECT 
            symbol,
            CURRENT_DATE, 
            ltp_avg_5d, ltp_avg_10d, ltp_avg_30d, ltp_avg_all,
            volume_avg_5d, volume_avg_10d, volume_avg_30d, volume_avg_all,
            vwap_avg_5d, vwap_avg_10d, vwap_avg_30d, vwap_avg_all,
            NOW()
        FROM averages
        ON CONFLICT (symbol) DO UPDATE SET
            "Date" = EXCLUDED."Date",
            ltp_avg_5d = EXCLUDED.ltp_avg_5d,
            ltp_avg_10d = EXCLUDED.ltp_avg_10d,
            ltp_avg_30d = EXCLUDED.ltp_avg_30d,
            ltp_avg_all = EXCLUDED.ltp_avg_all,
            volume_avg_5d = EXCLUDED.volume_avg_5d,
            volume_avg_10d = EXCLUDED.volume_avg_10d,
            volume_avg_30d = EXCLUDED.volume_avg_30d,
            volume_avg_all = EXCLUDED.volume_avg_all,
            vwap_avg_5d = EXCLUDED.vwap_avg_5d,
            vwap_avg_10d = EXCLUDED.vwap_avg_10d,
            vwap_avg_30d = EXCLUDED.vwap_avg_30d,
            vwap_avg_all = EXCLUDED.vwap_avg_all,
            updated_at = NOW();
    END;
    $function$;

    -- 3. Create the PnL Function
    CREATE OR REPLACE FUNCTION public.fn_cron_populate_profit_loss()
    RETURNS void
    LANGUAGE plpgsql
    AS $function$
    BEGIN
        WITH new_data AS (
            SELECT p.symbol,
                p."Current Balance" AS quantity,
                w."WACC Rate" AS wacc_rate,
                (p."Current Balance" * w."WACC Rate") AS total_investment,
                l."LTP" AS live_ltp,
                (p."Current Balance" * l."LTP"::numeric) AS current_value,
                (p."Current Balance" * l."LTP"::numeric - p."Current Balance" * w."WACC Rate") AS overall_profit_loss_amount,
                CASE
                    WHEN w."WACC Rate" > 0 THEN (l."LTP"::numeric - w."WACC Rate") / w."WACC Rate" * 100
                    ELSE 0
                END AS overall_profit_loss_percent,
                l.change_in_value AS daily_change_per_share,
                (p."Current Balance" * l.change_in_value::numeric) AS daily_gain_loss_amount,
                l.ltp_change_percent AS daily_gain_loss_percent
            FROM raw_meroshare_portfolio p
            LEFT JOIN raw_meroshare_wacc w ON p.symbol = w.symbol
            LEFT JOIN raw_nepseapi_live_prices l ON p.symbol = l.symbol
        )
        INSERT INTO public.wiki_profit_loss_analysis (
            symbol, quantity, wacc_rate, total_investment, live_ltp,
            current_value, overall_profit_loss_amount, overall_profit_loss_percent,
            daily_change_per_share, daily_gain_loss_amount, daily_gain_loss_percent,
            updated_at
        )
        SELECT 
            symbol, quantity, wacc_rate, total_investment, live_ltp,
            current_value, overall_profit_loss_amount, overall_profit_loss_percent,
            daily_change_per_share, daily_gain_loss_amount, daily_gain_loss_percent,
            CURRENT_TIMESTAMP
        FROM new_data
        ON CONFLICT (symbol) DO UPDATE SET
            quantity = EXCLUDED.quantity,
            wacc_rate = EXCLUDED.wacc_rate,
            total_investment = EXCLUDED.total_investment,
            live_ltp = EXCLUDED.live_ltp,
            current_value = EXCLUDED.current_value,
            overall_profit_loss_amount = EXCLUDED.overall_profit_loss_amount,
            overall_profit_loss_percent = EXCLUDED.overall_profit_loss_percent,
            daily_change_per_share = EXCLUDED.daily_change_per_share,
            daily_gain_loss_amount = EXCLUDED.daily_gain_loss_amount,
            daily_gain_loss_percent = EXCLUDED.daily_gain_loss_percent,
            updated_at = EXCLUDED.updated_at;
    END;
    $function$;

    -- 4. Unschedule if already exists to prevent duplicates
    """
    
    try:
        cur.execute(sql)
        
        # In Supabase, pg_cron functions are exposed in the cron schema
        unschedule_sql = """
        DO $$ 
        BEGIN 
            PERFORM cron.unschedule('sync-averages-daily'); 
        EXCEPTION WHEN OTHERS THEN 
            -- Ignore if it doesn't exist 
        END $$;
        
        DO $$ 
        BEGIN 
            PERFORM cron.unschedule('sync-pnl-5hours'); 
        EXCEPTION WHEN OTHERS THEN 
            -- Ignore if it doesn't exist 
        END $$;
        """
        cur.execute(unschedule_sql)
        
        schedule_sql = """
        SELECT cron.schedule('sync-averages-daily', '15 10 * * *', 'SELECT public.fn_cron_populate_averages();');
        SELECT cron.schedule('sync-pnl-5hours', '15 */5 * * *', 'SELECT public.fn_cron_populate_profit_loss();');
        """
        cur.execute(schedule_sql)
        
        print("Functions created and pg_cron jobs scheduled successfully.")
    except Exception as e:
        print(f"FAILED: {e}")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    setup_pg_cron()
