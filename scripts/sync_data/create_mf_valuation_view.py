import os
import psycopg2
from dotenv import load_dotenv

def create_view():
    load_dotenv()
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("DATABASE_URL not found in .env")
        return

    conn = psycopg2.connect(db_url)
    conn.autocommit = True
    cur = conn.cursor()

    try:
        print("Dropping old table and previous view...")
        cur.execute("DROP VIEW IF EXISTS vw_mf_asset_valuation_comparison CASCADE;")
        cur.execute("DROP VIEW IF EXISTS view_mf_summary_analytics CASCADE;")
        try:
            cur.execute("DROP TABLE IF EXISTS view_mf_assets_value_change CASCADE;")
        except psycopg2.errors.WrongObjectType:
            conn.rollback() # Rollback the failed transaction block
            cur.execute("DROP VIEW IF EXISTS view_mf_assets_value_change CASCADE;")
        
        print("Creating view view_mf_assets_value_change...")
        cur.execute("""
            CREATE OR REPLACE VIEW view_mf_assets_value_change AS
            SELECT 
                ast."MF",
                ast."symbol",
                ast."quantity",
                
                nav."Monthly_Nav_Date",
                nav."Weekly_Nav",
                
                nav."Weekly_Nav_Date",
                ph_week."Close" AS price_on_weekly_nav,
                (ast."quantity" * ph_week."Close") AS value_on_weekly_nav,
                
                live."lastTradedPrice" AS todays_ltp,
                (ast."quantity" * live."lastTradedPrice") AS value_today,
                
                (ast."quantity" * live."lastTradedPrice") - (ast."quantity" * ph_week."Close") AS value_change_since_weekly

            FROM raw_mf_nepsealpha_assets_lastmonth ast
            LEFT JOIN raw_mf_sharesansar_nav nav 
                ON ast."MF" = nav."symbol"
            LEFT JOIN raw_price_history ph_week 
                ON ast."symbol" = ph_week."symbol" 
                AND TO_DATE(nav."Weekly_Nav_Date", 'MM/DD/YYYY') = ph_week."Date"
            LEFT JOIN raw_nepseapi_live_prices live 
                ON ast."symbol" = live."symbol";
        """)
        
        print("Creating aggregated view view_mf_summary_analytics...")
        cur.execute("""
            CREATE OR REPLACE VIEW view_mf_summary_analytics AS
            WITH aggregated AS (
                SELECT
                    "MF",
                    
                    ROUND(SUM(value_on_weekly_nav)::numeric, 2) AS "last week value",
                    ROUND(SUM(value_today)::numeric, 2) AS "this week value",
                    ROUND(SUM(value_change_since_weekly)::numeric, 2) AS "change in value",
                    
                    ROUND((CASE WHEN SUM(value_on_weekly_nav) > 0 
                         THEN (SUM(value_change_since_weekly) / SUM(value_on_weekly_nav)) * 100 
                         ELSE 0 END)::numeric, 2) AS "value change percentate",
                    
                    SUM(CASE WHEN todays_ltp IS NULL OR price_on_weekly_nav IS NULL THEN quantity ELSE 0 END) AS "quantity without price",
                    SUM(quantity) AS "total quantity",
                         
                    MAX("Weekly_Nav_Date") AS "SS weekly Date",
                    ROUND(MAX("Weekly_Nav")::numeric, 2) AS "SS weekly NAV",
                    TRUE AS "NAV date Match Formula Date",
                    MAX("Monthly_Nav_Date") AS "Monthly Nav Month",
                    
                    COUNT(CASE WHEN price_on_weekly_nav IS NULL OR todays_ltp IS NULL THEN 1 END) AS "skipped scripts due to no price data"
                FROM view_mf_assets_value_change
                GROUP BY "MF"
            ),
            nav_calculated AS (
                SELECT 
                    agg.*,
                    alloc."Capital_Market",
                    alloc."Non_Capital_Market",
                    live_mf."lastTradedPrice" AS mf_ltp,
                    
                    ROUND((agg."SS weekly NAV" * (1 + (agg."value change percentate" / 100)))::numeric, 2) AS "adjusted_nav",
                    ROUND((agg."SS weekly NAV" * (1 + ((agg."value change percentate" / 100) * (alloc."Capital_Market" / 100))))::numeric, 2) AS "cap_market_adjusted_nav"
                    
                FROM aggregated agg
                LEFT JOIN raw_mf_nepsealpha_assets_allocation alloc
                    ON agg."MF" = alloc."symbol"
                LEFT JOIN raw_nepseapi_live_prices live_mf
                    ON agg."MF" = live_mf."symbol"
            )
            SELECT 
                n.*,
                
                ROUND((CASE WHEN "adjusted_nav" > 0 AND "adjusted_nav" IS NOT NULL
                     THEN ((mf_ltp - "adjusted_nav") / "adjusted_nav") * 100 
                     ELSE NULL END)::numeric, 2) AS "discount_premium_adjusted",
                     
                ROUND((CASE WHEN "cap_market_adjusted_nav" > 0 AND "cap_market_adjusted_nav" IS NOT NULL
                     THEN ((mf_ltp - "cap_market_adjusted_nav") / "cap_market_adjusted_nav") * 100 
                     ELSE NULL END)::numeric, 2) AS "discount_premium_cap_market"
            FROM nav_calculated n;
        """)
        print("Successfully recreated view_mf_assets_value_change and created view_mf_summary_analytics.")

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    create_view()
