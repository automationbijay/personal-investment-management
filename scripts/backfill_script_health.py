"""
One-off script that adds `updated_at` columns to legacy raw tables and populates the `sys_script_health` table with their latest timestamps.
"""

import os
import psycopg2
from dotenv import load_dotenv

def backfill_health():
    load_dotenv()
    db_url = os.getenv("DATABASE_URL")
    conn = psycopg2.connect(db_url)
    conn.autocommit = True
    cur = conn.cursor()

    try:
        # Step 1: Add updated_at to missing tables
        print("1. Adding updated_at to missing tables...")
        
        # raw_nepseapi_live_prices
        cur.execute("ALTER TABLE raw_nepseapi_live_prices ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP;")
        cur.execute("UPDATE raw_nepseapi_live_prices SET updated_at = last_updated_time WHERE updated_at IS NULL OR updated_at = CURRENT_TIMESTAMP;")
        print("Updated raw_nepseapi_live_prices.")

        # raw_price_history
        cur.execute("ALTER TABLE raw_price_history ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP;")
        # Backfill from created_at or default to current timestamp if missing
        cur.execute("UPDATE raw_price_history SET updated_at = created_at WHERE updated_at IS NULL OR updated_at = CURRENT_TIMESTAMP;")
        print("Updated raw_price_history.")

        # raw_mf_nepsealpha_assets_lastmonth
        cur.execute("ALTER TABLE raw_mf_nepsealpha_assets_lastmonth ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP;")
        cur.execute("UPDATE raw_mf_nepsealpha_assets_lastmonth SET updated_at = created_at WHERE updated_at IS NULL OR updated_at = CURRENT_TIMESTAMP;")
        print("Updated raw_mf_nepsealpha_assets_lastmonth.")

        # Step 2: Query all raw_ tables and get MAX(updated_at)
        print("\n2. Backfilling sys_script_health table...")
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name LIKE 'raw_%';
        """)
        tables = cur.fetchall()

        for t in tables:
            t_name = t[0]
            # Map script names:
            if t_name == 'raw_securities':
                script_name = 'sync_securities.py'
            elif t_name == 'raw_mf_sharesansar_nav':
                script_name = 'sync_sharesansar_nav.py'
            else:
                script_name = f'sync_{t_name}.py'
            
            # Fetch MAX(updated_at)
            try:
                cur.execute(f"SELECT MAX(updated_at) FROM {t_name};")
                res = cur.fetchone()
                max_updated = res[0] if res and res[0] else None
                
                if max_updated:
                    # Upsert into sys_script_health
                    cur.execute("""
                        INSERT INTO sys_script_health (script_name, last_run, health_status, updated_at)
                        VALUES (%s, %s, 'SUCCESS', %s)
                        ON CONFLICT (script_name) DO UPDATE SET
                            last_run = EXCLUDED.last_run,
                            health_status = EXCLUDED.health_status,
                            updated_at = EXCLUDED.updated_at;
                    """, (script_name, max_updated, max_updated))
                    print(f"Logged {script_name} with last_run = {max_updated}")
                else:
                    print(f"Table {t_name} is empty or has no updated_at value.")
            except Exception as inner_e:
                print(f"Error processing {t_name}: {inner_e}")

        print("\nBackfill complete.")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    backfill_health()
