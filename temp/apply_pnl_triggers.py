import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
db_url = os.getenv("DATABASE_URL")
conn = psycopg2.connect(db_url)
cur = conn.cursor()

trigger_sql = """
CREATE OR REPLACE FUNCTION public.fn_sync_wiki_profit_loss()
RETURNS trigger
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
        WHERE p.symbol = NEW.symbol
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

    RETURN NEW;
END;
$function$;

DROP TRIGGER IF EXISTS trg_sync_pnl_meroshare ON public.raw_meroshare_portfolio;
CREATE TRIGGER trg_sync_pnl_meroshare
AFTER INSERT OR UPDATE ON public.raw_meroshare_portfolio
FOR EACH ROW EXECUTE FUNCTION public.fn_sync_wiki_profit_loss();

DROP TRIGGER IF EXISTS trg_sync_pnl_live_prices ON public.raw_nepseapi_live_prices;
CREATE TRIGGER trg_sync_pnl_live_prices
AFTER INSERT OR UPDATE ON public.raw_nepseapi_live_prices
FOR EACH ROW EXECUTE FUNCTION public.fn_sync_wiki_profit_loss();
"""

try:
    cur.execute(trigger_sql)
    conn.commit()
    print("Triggers and function created successfully!")
except Exception as e:
    conn.rollback()
    print(f"FAILED: {e}")
finally:
    cur.close()
    conn.close()
