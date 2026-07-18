import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
db_url = os.getenv("DATABASE_URL")

conn = psycopg2.connect(db_url)
conn.autocommit = True
cur = conn.cursor()

indexes_to_drop = [
    # raw_securities
    "raw_securities_symbol_key",
    "idx_raw_securities_symbol",
    # fundamental_data
    "fundamental_data_symbol_key",
    "idx_fundamental_data_symbol",
    # raw_deb_nepsealpha_details
    "idx_raw_deb_nepsealpha_symbol",
    # raw_deb_nepseapi_marketdepth
    "idx_raw_deb_marketdepth_symbol",
    # raw_meroshare_portfolio
    "idx_raw_meroshare_portfolio_scrip",
    # raw_meroshare_wacc
    "idx_raw_meroshare_wacc_scrip_name",
    # raw_mf_sharesansar_nav
    "idx_raw_mf_sharesansar_nav_symbol",
    # raw_mf_nepsealpha_assets_allocation
    "idx_raw_mf_assets_allocation_symbol",
    # raw_nepseapi_live_prices
    "idx_raw_live_prices_symbol",
    # raw_price_history
    "unique_symbol_date",
    "idx_raw_price_history_symbol",
    # mf_assets_value_change
    "idx_mf_assets_value_change_mf",
    # raw_mf_nepsealpha_assets_lastmonth
    "idx_raw_mf_nepsealpha_assets_lastmonth_mf"
]

for idx in indexes_to_drop:
    try:
        cur.execute(f"DROP INDEX IF EXISTS public.{idx};")
        print(f"Dropped index: {idx}")
    except Exception as e:
        print(f"Error dropping {idx}: {e}")

# Add missing foreign key index
try:
    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_mf_assets_value_change_nav_date 
        ON public.mf_assets_value_change USING btree (weekly_nav_date_actual);
    """)
    print("Created index: idx_mf_assets_value_change_nav_date")
except Exception as e:
    print(f"Error creating index on weekly_nav_date_actual: {e}")

conn.close()
print("Index modifications complete.")
