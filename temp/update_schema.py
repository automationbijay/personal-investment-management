import os
import psycopg2
from dotenv import load_dotenv
import subprocess

def main():
    load_dotenv()
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("DATABASE_URL not found in .env")
        return

    conn = psycopg2.connect(db_url)
    conn.autocommit = True
    cur = conn.cursor()

    try:
        print("1. Dropping dependent views...")
        cur.execute("DROP VIEW IF EXISTS view_mf_summary_analytics CASCADE;")
        try:
            cur.execute("DROP VIEW IF EXISTS view_mf_assets_value_change CASCADE;")
        except psycopg2.errors.WrongObjectType:
            conn.rollback()
            cur.execute("DROP TABLE IF EXISTS view_mf_assets_value_change CASCADE;")

        print("2. Altering raw_nepseapi_live_prices table columns...")
        # Rename existing columns
        alter_statements = [
            'ALTER TABLE public.raw_nepseapi_live_prices RENAME COLUMN "LTP" TO "lastTradedPrice";',
            'ALTER TABLE public.raw_nepseapi_live_prices RENAME COLUMN previous_close TO "previousClose";',
            'ALTER TABLE public.raw_nepseapi_live_prices RENAME COLUMN turnover TO "totalTradeValue";',
            'ALTER TABLE public.raw_nepseapi_live_prices RENAME COLUMN ltp_change_percent TO "percentageChange";',
            'ALTER TABLE public.raw_nepseapi_live_prices RENAME COLUMN last_updated_time TO "lastUpdatedDateTime";'
        ]
        
        for stmt in alter_statements:
            try:
                cur.execute(stmt)
                print(f"Executed: {stmt}")
            except psycopg2.errors.UndefinedColumn:
                # Column might have been renamed already
                print(f"Skipping (might be renamed already): {stmt}")
            
        print("Dropping change_in_value...")
        try:
            cur.execute('ALTER TABLE public.raw_nepseapi_live_prices DROP COLUMN change_in_value;')
        except psycopg2.errors.UndefinedColumn:
            print("change_in_value already dropped.")

        print("Adding new columns from API...")
        new_columns = {
            '"securityId"': 'text',
            '"securityName"': 'text',
            '"indexId"': 'numeric',
            '"openPrice"': 'numeric',
            '"highPrice"': 'numeric',
            '"lowPrice"': 'numeric',
            '"totalTradeQuantity"': 'numeric',
            '"lastTradedVolume"': 'numeric',
            '"averageTradedPrice"': 'numeric'
        }
        for col, dtype in new_columns.items():
            try:
                cur.execute(f"ALTER TABLE public.raw_nepseapi_live_prices ADD COLUMN IF NOT EXISTS {col} {dtype};")
                print(f"Added column {col}")
            except Exception as e:
                print(f"Could not add {col}: {e}")

        print("3. Recreating functions...")
        
        fn_sync = """
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
                    l."lastTradedPrice" AS live_ltp,
                    (p."Current Balance" * l."lastTradedPrice"::numeric) AS current_value,
                    (p."Current Balance" * l."lastTradedPrice"::numeric - p."Current Balance" * w."WACC Rate") AS overall_profit_loss_amount,
                    CASE
                        WHEN w."WACC Rate" > 0 THEN (l."lastTradedPrice"::numeric - w."WACC Rate") / w."WACC Rate" * 100
                        ELSE 0
                    END AS overall_profit_loss_percent,
                    (l."lastTradedPrice"::numeric - l."previousClose"::numeric) AS daily_change_per_share,
                    (p."Current Balance" * (l."lastTradedPrice"::numeric - l."previousClose"::numeric)) AS daily_gain_loss_amount,
                    l."percentageChange" AS daily_gain_loss_percent
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
        """
        cur.execute(fn_sync)
        
        fn_cron = """
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
                    l."lastTradedPrice" AS live_ltp,
                    (p."Current Balance" * l."lastTradedPrice"::numeric) AS current_value,
                    (p."Current Balance" * l."lastTradedPrice"::numeric - p."Current Balance" * w."WACC Rate") AS overall_profit_loss_amount,
                    CASE
                        WHEN w."WACC Rate" > 0 THEN (l."lastTradedPrice"::numeric - w."WACC Rate") / w."WACC Rate" * 100
                        ELSE 0
                    END AS overall_profit_loss_percent,
                    (l."lastTradedPrice"::numeric - l."previousClose"::numeric) AS daily_change_per_share,
                    (p."Current Balance" * (l."lastTradedPrice"::numeric - l."previousClose"::numeric)) AS daily_gain_loss_amount,
                    l."percentageChange" AS daily_gain_loss_percent
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
        """
        cur.execute(fn_cron)

        print("4. Recreating views by running create_mf_valuation_view.py...")
        result = subprocess.run(
            ["python", "scripts/sync_data/create_mf_valuation_view.py"],
            capture_output=True,
            text=True
        )
        print("View script output:", result.stdout)
        if result.stderr:
            print("View script errors:", result.stderr)
            
        print("Schema update completed successfully.")

    except Exception as e:
        print(f"Error during schema update: {e}")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    main()
