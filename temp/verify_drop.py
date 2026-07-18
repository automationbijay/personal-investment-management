import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
db_url = os.environ.get("DATABASE_URL")
if not db_url:
    print("DATABASE_URL not found")
    exit(1)

conn = psycopg2.connect(db_url)
cur = conn.cursor()

# Check table
cur.execute("SELECT 1 FROM pg_tables WHERE schemaname = 'public' AND tablename = 'mf_assets_analytics';")
table_exists = cur.fetchone() is not None

# Check functions
cur.execute("""
    SELECT proname 
    FROM pg_proc p
    JOIN pg_namespace n ON n.oid = p.pronamespace
    WHERE n.nspname = 'public' 
    AND proname IN (
        'fn_refresh_mf_assets_analytics',
        'fn_sync_alloc_to_mf_analytics',
        'fn_sync_mf_nav_date',
        'fn_sync_nav_to_mf_analytics',
        'fn_sync_price_to_mf_analytics',
        'fn_calculate_mf_asset_ltps',
        'fn_fetch_nav_date_on_insert'
    );
""")
functions = cur.fetchall()

if table_exists:
    print("WARNING: Table mf_assets_analytics still exists!")
else:
    print("SUCCESS: Table mf_assets_analytics is removed.")

if functions:
    print(f"WARNING: The following functions still exist: {[f[0] for f in functions]}")
else:
    print("SUCCESS: All obsolete functions are removed.")

cur.close()
conn.close()
