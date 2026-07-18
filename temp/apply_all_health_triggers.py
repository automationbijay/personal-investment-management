import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
db_url = os.getenv('DATABASE_URL')

if not db_url:
    print('No DATABASE_URL found.')
    exit(1)

tables = [
    'raw_deb_nepsealpha_details',
    'raw_deb_nepseapi_marketdepth',
    'raw_meroshare_portfolio',
    'raw_meroshare_wacc',
    'raw_mf_nepsealpha_assets_allocation',
    'raw_mf_nepsealpha_assets_lastmonth',
    'raw_mf_nepsealpha_details',
    'raw_mf_sharesansar_nav',
    'raw_mutual_funds',
    'raw_nepseapi_live_prices',
    'raw_price_history',
    'raw_securities'
]

function_sql = """
CREATE OR REPLACE FUNCTION trg_update_script_health()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO sys_script_health (table_name, last_run, health_status, updated_at, script_ran_from)
    VALUES (TG_TABLE_NAME, NOW(), 'SUCCESS (Auto-Trigger)', NOW(), 'db_trigger')
    ON CONFLICT (table_name)
    DO UPDATE SET
        last_run = EXCLUDED.last_run,
        health_status = EXCLUDED.health_status,
        updated_at = EXCLUDED.updated_at,
        script_ran_from = EXCLUDED.script_ran_from;
        
    RETURN NULL; -- For AFTER STATEMENT trigger, return NULL
END;
$$ LANGUAGE plpgsql;
"""

try:
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()
    
    # 1. Create the function
    print("Creating function trg_update_script_health...")
    cur.execute(function_sql)
    
    # 2. Add trigger to all tables
    for table in tables:
        print(f"Applying trigger to {table}...")
        cur.execute(f"DROP TRIGGER IF EXISTS trg_auto_health ON {table};")
        cur.execute(f"""
            CREATE TRIGGER trg_auto_health
            AFTER INSERT OR UPDATE ON {table}
            FOR EACH STATEMENT
            EXECUTE FUNCTION trg_update_script_health();
        """)
        
    conn.commit()
    print("Successfully applied triggers to all raw tables.")
    
    cur.close()
    conn.close()
except Exception as e:
    print('Error applying migration:', e)
