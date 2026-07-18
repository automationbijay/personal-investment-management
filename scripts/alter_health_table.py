"""
One-off migration script that modified the schema of `sys_script_health` (renaming columns, adding source URL tracking).
"""

import os
import psycopg2
from dotenv import load_dotenv

def alter_health_table():
    load_dotenv()
    db_url = os.getenv("DATABASE_URL")
    conn = psycopg2.connect(db_url)
    conn.autocommit = True
    cur = conn.cursor()

    try:
        print("1. Renaming script_name to table_name...")
        # Check if column exists before renaming
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='sys_script_health' AND column_name='script_name';
        """)
        if cur.fetchone():
            cur.execute("ALTER TABLE sys_script_health RENAME COLUMN script_name TO table_name;")
            print("Renamed column to table_name.")
        else:
            print("Column script_name not found or already renamed.")

        print("2. Adding source_page_url and script_ran_from columns...")
        cur.execute("ALTER TABLE sys_script_health ADD COLUMN IF NOT EXISTS source_page_url TEXT;")
        cur.execute("ALTER TABLE sys_script_health ADD COLUMN IF NOT EXISTS script_ran_from TEXT;")
        print("Added new columns.")

        print("3. Updating values in table_name...")
        cur.execute("SELECT table_name FROM sys_script_health;")
        rows = cur.fetchall()
        for row in rows:
            old_val = row[0]
            new_val = old_val
            if new_val.startswith('sync_'):
                new_val = new_val[5:] # remove 'sync_'
            if new_val.endswith('.py'):
                new_val = new_val[:-3] # remove '.py'
            
            # Specific mappings if needed
            if old_val == 'sync_securities.py':
                new_val = 'raw_securities'
            elif old_val == 'sync_sharesansar_nav.py':
                new_val = 'raw_mf_sharesansar_nav'

            if old_val != new_val:
                cur.execute("UPDATE sys_script_health SET table_name = %s WHERE table_name = %s;", (new_val, old_val))
                print(f"Updated {old_val} to {new_val}")
        
        print("Update complete.")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    alter_health_table()
