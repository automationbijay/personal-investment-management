import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
db_url = os.environ.get("DATABASE_URL")
if not db_url:
    print("DATABASE_URL not found")
    exit(1)

conn = psycopg2.connect(db_url)
conn.autocommit = True
cur = conn.cursor()

commands = [
    """
    CREATE OR REPLACE VIEW public.mf_assets_value_change WITH (security_invoker = true) AS
     SELECT ast."MF",
        ast.symbol,
        ast.quantity,
        nav."Monthly_Nav_Date",
        nav."Weekly_Nav",
        nav."Weekly_Nav_Date",
        ph_week."Close" AS price_on_weekly_nav,
        ((ast.quantity)::numeric * ph_week."Close") AS value_on_weekly_nav,
        live."LTP" AS todays_ltp,
        ((ast.quantity)::numeric * live."LTP") AS value_today,
        (((ast.quantity)::numeric * live."LTP") - ((ast.quantity)::numeric * ph_week."Close")) AS value_change_since_weekly
       FROM (((raw_mf_nepsealpha_assets_lastmonth ast
         LEFT JOIN raw_mf_sharesansar_nav nav ON ((ast."MF" = nav.symbol)))
         LEFT JOIN raw_price_history ph_week ON (((ast.symbol = ph_week.symbol) AND (to_date(nav."Weekly_Nav_Date", 'MM/DD/YYYY'::text) = ph_week."Date"))))
         LEFT JOIN raw_nepseapi_live_prices live ON ((ast.symbol = live.symbol)));
    """,
    """
    CREATE OR REPLACE VIEW public.vw_mf_summary_analytics WITH (security_invoker = true) AS
     WITH aggregated AS (
             SELECT mf_assets_value_change."MF",
                round(sum(mf_assets_value_change.value_on_weekly_nav), 2) AS "last week value",
                round(sum(mf_assets_value_change.value_today), 2) AS "this week value",
                round(sum(mf_assets_value_change.value_change_since_weekly), 2) AS "change in value",
                round(
                    CASE
                        WHEN (sum(mf_assets_value_change.value_on_weekly_nav) > (0)::numeric) THEN ((sum(mf_assets_value_change.value_change_since_weekly) / sum(mf_assets_value_change.value_on_weekly_nav)) * (100)::numeric)
                        ELSE (0)::numeric
                    END, 2) AS "value change percentate",
                sum(
                    CASE
                        WHEN ((mf_assets_value_change.todays_ltp IS NULL) OR (mf_assets_value_change.price_on_weekly_nav IS NULL)) THEN mf_assets_value_change.quantity
                        ELSE 0
                    END) AS "quantity without price",
                sum(mf_assets_value_change.quantity) AS "total quantity",
                max(mf_assets_value_change."Weekly_Nav_Date") AS "SS weekly Date",
                round(max(mf_assets_value_change."Weekly_Nav"), 2) AS "SS weekly NAV",
                true AS "NAV date Match Formula Date",
                max(mf_assets_value_change."Monthly_Nav_Date") AS "Monthly Nav Month",
                count(
                    CASE
                        WHEN ((mf_assets_value_change.price_on_weekly_nav IS NULL) OR (mf_assets_value_change.todays_ltp IS NULL)) THEN 1
                        ELSE NULL::integer
                    END) AS "skipped scripts due to no price data"
               FROM mf_assets_value_change
              GROUP BY mf_assets_value_change."MF"
            ), nav_calculated AS (
             SELECT agg."MF",
                agg."last week value",
                agg."this week value",
                agg."change in value",
                agg."value change percentate",
                agg."quantity without price",
                agg."total quantity",
                agg."SS weekly Date",
                agg."SS weekly NAV",
                agg."NAV date Match Formula Date",
                agg."Monthly Nav Month",
                agg."skipped scripts due to no price data",
                alloc."Capital_Market",
                alloc."Non_Capital_Market",
                live_mf."LTP" AS mf_ltp,
                round((agg."SS weekly NAV" * ((1)::numeric + (agg."value change percentate" / (100)::numeric))), 2) AS adjusted_nav,
                round((agg."SS weekly NAV" * ((1)::numeric + ((agg."value change percentate" / (100)::numeric) * (alloc."Capital_Market" / (100)::numeric)))), 2) AS cap_market_adjusted_nav
               FROM ((aggregated agg
                 LEFT JOIN raw_mf_nepsealpha_assets_allocation alloc ON ((agg."MF" = alloc.symbol)))
                 LEFT JOIN raw_nepseapi_live_prices live_mf ON ((agg."MF" = live_mf.symbol)))
            )
     SELECT "MF",
        "last week value",
        "this week value",
        "change in value",
        "value change percentate",
        "quantity without price",
        "total quantity",
        "SS weekly Date",
        "SS weekly NAV",
        "NAV date Match Formula Date",
        "Monthly Nav Month",
        "skipped scripts due to no price data",
        "Capital_Market",
        "Non_Capital_Market",
        mf_ltp,
        adjusted_nav,
        cap_market_adjusted_nav,
        round(
            CASE
                WHEN ((adjusted_nav > (0)::numeric) AND (adjusted_nav IS NOT NULL)) THEN (((mf_ltp - adjusted_nav) / adjusted_nav) * (100)::numeric)
                ELSE NULL::numeric
            END, 2) AS discount_premium_adjusted,
        round(
            CASE
                WHEN ((cap_market_adjusted_nav > (0)::numeric) AND (cap_market_adjusted_nav IS NOT NULL)) THEN (((mf_ltp - cap_market_adjusted_nav) / cap_market_adjusted_nav) * (100)::numeric)
                ELSE NULL::numeric
            END, 2) AS discount_premium_cap_market
       FROM nav_calculated n;
    """
]

for cmd in commands:
    print("Executing view recreation...")
    cur.execute(cmd)

print("Views updated successfully.")
cur.close()
conn.close()
