import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
conn = psycopg2.connect(os.getenv('DATABASE_URL'))
conn.autocommit = False
cur = conn.cursor()

try:
    # 1. Rename Columns
    column_renames = [
        ("deb_ytm_analysis", "Symbol", "symbol"),
        ("mf_assets_analytics", "Symbol", "symbol"),
        ("mf_assets_value_change", "Symbol", "symbol"),
        ("raw_deb_marketdepth", "Symbol", "symbol"),
        ("raw_deb_nepsealpha", "Symbol", "symbol"),
        ("raw_live_prices", "Symbol", "symbol"),
        ("raw_meroshare_portfolio", "Scrip", "symbol"),
        ("raw_meroshare_wacc", "Scrip Name", "symbol"),
        ("raw_mf_assets_allocation", "Symbol", "symbol"),
        ("raw_mf_nepsealpha_assets_lastmonth", "Symbol", "symbol"),
        ("raw_mf_sharesansar_nav", "Symbol", "symbol"),
        ("raw_price_history", "Symbol", "symbol")
    ]
    
    for table, old_col, new_col in column_renames:
        print(f"Renaming {table}.\"{old_col}\" to {new_col}...")
        cur.execute(f'ALTER TABLE public."{table}" RENAME COLUMN "{old_col}" TO "{new_col}";')

    # 2. Rename Tables
    table_renames = [
        ("raw_live_prices", "raw_nepseapi_live_prices"),
        ("raw_deb_marketdepth", "raw_deb_nepseapi_marketdepth"),
        ("raw_mf_assets_allocation", "raw_mf_nepsealpha_assets_allocation"),
        ("raw_deb_nepsealpha", "raw_deb_nepsealpha_details")
    ]

    for old_tbl, new_tbl in table_renames:
        print(f"Renaming table {old_tbl} to {new_tbl}...")
        cur.execute(f'ALTER TABLE public."{old_tbl}" RENAME TO "{new_tbl}";')

    # Recreate the view vw_live_vs_history_price since it might have issues if we don't recreate it?
    # Actually, Postgres automatically updates view column references for simple renames! 
    # Let's check if we need to manually update functions next.

    conn.commit()
    print("All renames executed successfully.")

except Exception as e:
    conn.rollback()
    print(f"Error occurred: {e}")

cur.close()
conn.close()
