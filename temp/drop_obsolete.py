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
    "DROP TABLE IF EXISTS public.mf_assets_analytics CASCADE;",
    "DROP FUNCTION IF EXISTS public.fn_refresh_mf_assets_analytics() CASCADE;",
    "DROP FUNCTION IF EXISTS public.fn_sync_alloc_to_mf_analytics() CASCADE;",
    "DROP FUNCTION IF EXISTS public.fn_sync_mf_nav_date() CASCADE;",
    "DROP FUNCTION IF EXISTS public.fn_sync_nav_to_mf_analytics() CASCADE;",
    "DROP FUNCTION IF EXISTS public.fn_sync_price_to_mf_analytics() CASCADE;",
    "DROP FUNCTION IF EXISTS public.fn_calculate_mf_asset_ltps() CASCADE;",
    "DROP FUNCTION IF EXISTS public.fn_fetch_nav_date_on_insert() CASCADE;"
]

for cmd in commands:
    print(f"Executing: {cmd}")
    cur.execute(cmd)

print("Cleanup completed successfully.")
cur.close()
conn.close()
