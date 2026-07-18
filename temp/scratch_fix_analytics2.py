import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor()

sql = """
CREATE OR REPLACE FUNCTION public.fn_refresh_mf_assets_analytics()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
        DECLARE
            v_today_ltp REAL;
        BEGIN
            -- Fetch most recent LTP from raw_price_history
            SELECT "LTP" INTO v_today_ltp 
            FROM public.raw_price_history 
            WHERE symbol = COALESCE(NEW."MF", OLD."MF")
            ORDER BY "Date" DESC LIMIT 1;

            INSERT INTO public.mf_assets_analytics (
                "Pkey", symbol, "Month", "total_weekly_value", "total_current_value", "total_change", "weighted_avg_change_pct", 
                "capital_market_adj_change_pct", "Today_NAV", "Today_LTP", "Premium_Discount_Pct",
                "sharesansar_Mutual_Fund_Name", "sharesansar_Weekly_Nav", "sharesansar_Weekly_Nav_Date", "sharesansar_Monthly_Nav", "sharesansar_Monthly_Nav_Date", "sharesansar_LTP",
                "nepsealpha_Date_Till", "nepsealpha_Fixed_Income", "nepsealpha_Cash", "nepsealpha_Capital_Market", "nepsealpha_Non_Capital_Market",
                "both_source_has_same_month",
                "updated_at"
            )
            WITH agg AS (
                SELECT 
                    mvc."MF", 
                    mvc."Month", 
                    SUM(COALESCE(mvc."weekly Nav Value", mvc."today's Nav Value", 0)) as total_weekly, 
                    SUM(COALESCE(mvc."today's Nav Value", mvc."weekly Nav Value", 0)) as total_current, 
                    SUM(COALESCE(mvc."nav changed", 0)) as total_change,
                    alloc."Capital_Market",
                    nav."Weekly_Nav",
                    nav."LTP" as sharesansar_ltp,
                    rmf.mutual_fund_name as "Mutual_Fund_Name", 
                    nav."Weekly_Nav_Date", nav."Monthly_Nav", nav."Monthly_Nav_Date",
                    alloc."Date_Till", alloc."Fixed_Income", alloc."Cash", alloc."Non_Capital_Market"
                FROM public.mf_assets_value_change mvc
                LEFT JOIN public.raw_mf_sharesansar_nav nav ON mvc."MF" = nav.symbol
                LEFT JOIN public.raw_mutual_funds rmf ON mvc."MF" = rmf.symbol
                LEFT JOIN public.raw_mf_nepsealpha_assets_allocation alloc ON mvc."MF" = alloc.symbol
                WHERE mvc."MF" = COALESCE(NEW."MF", OLD."MF")
                AND mvc."Month" = COALESCE(NEW."Month", OLD."Month")
                GROUP BY mvc."MF", mvc."Month", alloc."Capital_Market", nav."Weekly_Nav", nav."LTP", rmf.mutual_fund_name, nav."Weekly_Nav_Date", nav."Monthly_Nav", nav."Monthly_Nav_Date", alloc."Date_Till", alloc."Fixed_Income", alloc."Cash", alloc."Non_Capital_Market"
            ),
            calc AS (
                SELECT 
                    *,
                    CASE 
                        WHEN total_weekly != 0 
                        THEN (total_change / total_weekly) * 100 
                        ELSE NULL 
                    END as weighted_avg_change_pct,
                    CASE
                        WHEN total_weekly != 0 AND "Capital_Market" IS NOT NULL
                        THEN ((total_change / total_weekly) * 100) * ("Capital_Market" / 100.0)
                        ELSE 0
                    END as capital_market_adj_change_pct
                FROM agg
            ),
            final_calc AS (
                SELECT 
                    *,
                    "Weekly_Nav" * (1 + capital_market_adj_change_pct / 100.0) as "Today_NAV"
                FROM calc
            )
            SELECT 
                "MF" || '-' || "Month",
                "MF", "Month", total_weekly, total_current, total_change, weighted_avg_change_pct, capital_market_adj_change_pct,
                "Today_NAV",
                v_today_ltp,
                CASE 
                    WHEN "Today_NAV" != 0 AND "Today_NAV" IS NOT NULL
                    THEN ((COALESCE(v_today_ltp, sharesansar_ltp) - "Today_NAV") / "Today_NAV") * 100
                    ELSE NULL
                END,
                "Mutual_Fund_Name", "Weekly_Nav", "Weekly_Nav_Date", "Monthly_Nav", "Monthly_Nav_Date", sharesansar_ltp,
                "Date_Till", "Fixed_Income", "Cash", "Capital_Market", "Non_Capital_Market",
                (LOWER(REGEXP_REPLACE("Month", '[^a-zA-Z]', '', 'g')) = LOWER(REGEXP_REPLACE("Monthly_Nav_Date", '[^a-zA-Z]', '', 'g'))),
                NOW()
            FROM final_calc
            ON CONFLICT ("Pkey") DO UPDATE SET
                symbol = EXCLUDED.symbol,
                "Month" = EXCLUDED."Month",
                "total_weekly_value" = EXCLUDED."total_weekly_value",
                "total_current_value" = EXCLUDED."total_current_value",
                "total_change" = EXCLUDED."total_change",
                "weighted_avg_change_pct" = EXCLUDED."weighted_avg_change_pct",
                "capital_market_adj_change_pct" = EXCLUDED."capital_market_adj_change_pct",
                "Today_NAV" = EXCLUDED."Today_NAV",
                "Today_LTP" = EXCLUDED."Today_LTP",
                "Premium_Discount_Pct" = EXCLUDED."Premium_Discount_Pct",
                "sharesansar_Mutual_Fund_Name" = EXCLUDED."sharesansar_Mutual_Fund_Name",
                "sharesansar_Weekly_Nav" = EXCLUDED."sharesansar_Weekly_Nav",
                "sharesansar_Weekly_Nav_Date" = EXCLUDED."sharesansar_Weekly_Nav_Date",
                "sharesansar_Monthly_Nav" = EXCLUDED."sharesansar_Monthly_Nav",
                "sharesansar_Monthly_Nav_Date" = EXCLUDED."sharesansar_Monthly_Nav_Date",
                "sharesansar_LTP" = EXCLUDED."sharesansar_LTP",
                "nepsealpha_Date_Till" = EXCLUDED."nepsealpha_Date_Till",
                "nepsealpha_Fixed_Income" = EXCLUDED."nepsealpha_Fixed_Income",
                "nepsealpha_Cash" = EXCLUDED."nepsealpha_Cash",
                "nepsealpha_Capital_Market" = EXCLUDED."nepsealpha_Capital_Market",
                "nepsealpha_Non_Capital_Market" = EXCLUDED."nepsealpha_Non_Capital_Market",
                "both_source_has_same_month" = EXCLUDED."both_source_has_same_month",
                "updated_at" = EXCLUDED."updated_at";
            
            RETURN NULL;
        END;
        $function$
;
"""

try:
    cur.execute(sql)
    conn.commit()
    print("Fixed fn_refresh_mf_assets_analytics trigger!")
except Exception as e:
    conn.rollback()
    print(f"Error: {e}")
    
cur.close()
conn.close()
