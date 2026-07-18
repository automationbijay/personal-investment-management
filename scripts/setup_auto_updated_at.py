"""
Enables the `moddatetime` PostgreSQL extension and applies triggers to automatically update `updated_at` columns whenever a row is modified.
"""

import os
import psycopg2
from dotenv import load_dotenv

def setup_auto_updated_at():
    load_dotenv()
    db_url = os.getenv("DATABASE_URL")
    conn = psycopg2.connect(db_url)
    conn.autocommit = True
    cur = conn.cursor()

    try:
        print("Enabling moddatetime extension...")
        cur.execute("CREATE EXTENSION IF NOT EXISTS moddatetime;")
        
        print("Fetching all tables with an 'updated_at' column...")
        cur.execute("""
            SELECT c.table_name 
            FROM information_schema.columns c
            JOIN information_schema.tables t 
              ON c.table_schema = t.table_schema 
             AND c.table_name = t.table_name
            WHERE c.table_schema = 'public' 
            AND c.column_name = 'updated_at'
            AND t.table_type = 'BASE TABLE';
        """)
        tables = cur.fetchall()
        
        for t in tables:
            table_name = t[0]
            trigger_name = f"trg_auto_update_{table_name}"
            
            print(f"Applying auto-update trigger to {table_name}...")
            
            # Drop existing trigger if it exists to avoid duplicates
            cur.execute(f"DROP TRIGGER IF EXISTS {trigger_name} ON {table_name};")
            
            # Create the trigger
            cur.execute(f"""
                CREATE TRIGGER {trigger_name}
                BEFORE UPDATE ON {table_name}
                FOR EACH ROW
                EXECUTE FUNCTION moddatetime(updated_at);
            """)
            
        print(f"\nSuccessfully applied auto-updating triggers to {len(tables)} tables!")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    setup_auto_updated_at()
