import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor()

functions_to_update = [
    'generate_tms_order_urls',
    'refresh_urls_on_config_update',
    'fn_refresh_mf_assets_analytics',
    'fn_sync_price_to_mf_analytics',
    'fn_sync_alloc_to_mf_analytics',
    'fn_sync_nav_to_mf_analytics',
    'fn_sync_analytics_from_raw',
    'fn_calculate_mf_asset_ltps',
    'fn_update_mf_analytics_on_price_change',
    'fn_sync_mf_nav_date',
    'fn_fetch_nav_date_on_insert'
]

with open('backup_functions.sql', 'w', encoding='utf-8') as f:
    for func in functions_to_update:
        cur.execute("SELECT pg_get_functiondef(oid) FROM pg_proc WHERE proname = %s;", (func,))
        row = cur.fetchone()
        if row:
            f.write(row[0] + ";\n\n")

cur.close()
conn.close()
