import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.environ.get("DATABASE_URL")

sql = """
CREATE OR REPLACE VIEW vw_profit_loss_analysis WITH (security_invoker = true) AS
SELECT 
    p.symbol,
    p."Current Balance" AS quantity,
    w."WACC Rate" AS wacc_rate,
    (p."Current Balance" * w."WACC Rate") AS total_investment,
    l."LTP" AS live_ltp,
    (p."Current Balance" * l."LTP") AS current_value,
    -- Overall Profit/Loss
    ((p."Current Balance" * l."LTP") - (p."Current Balance" * w."WACC Rate")) AS overall_profit_loss_amount,
    CASE 
        WHEN w."WACC Rate" > 0 THEN ((l."LTP" - w."WACC Rate") / w."WACC Rate") * 100 
        ELSE 0 
    END AS overall_profit_loss_percent,
    -- Daily Gain/Loss
    l."change_in_value" AS daily_change_per_share,
    (p."Current Balance" * l."change_in_value") AS daily_gain_loss_amount,
    l."ltp_change_percent" AS daily_gain_loss_percent
FROM 
    raw_meroshare_portfolio p
LEFT JOIN 
    raw_meroshare_wacc w ON p.symbol = w.symbol
LEFT JOIN 
    raw_nepseapi_live_prices l ON p.symbol = l.symbol;
"""

def main():
    conn = psycopg2.connect(DATABASE_URL)
    conn.autocommit = True
    cur = conn.cursor()
    try:
        print("Creating view vw_profit_loss_analysis...")
        cur.execute(sql)
        print("View created successfully.")
        
        # Let's test the view by fetching 5 rows
        cur.execute("SELECT * FROM vw_profit_loss_analysis LIMIT 5;")
        rows = cur.fetchall()
        print("\nSample Output:")
        col_names = [desc[0] for desc in cur.description]
        print(" | ".join(col_names))
        for row in rows:
            print(row)
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    main()
