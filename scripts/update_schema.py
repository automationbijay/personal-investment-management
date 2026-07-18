"""
Migration script that established Primary Keys and Foreign Key relationships between the raw price/NAV tables and `raw_securities`.
"""

import os
import psycopg2
from dotenv import load_dotenv

def update_schema():
    load_dotenv()
    db_url = os.getenv("DATABASE_URL")
    conn = psycopg2.connect(db_url)
    conn.autocommit = True
    cur = conn.cursor()

    try:
        print("1. Changing primary key of raw_securities to 'symbol'...")
        # Drop the existing primary key on 'id'.
        # The constraint name is usually 'raw_securities_pkey'
        cur.execute("""
            ALTER TABLE raw_securities DROP CONSTRAINT IF EXISTS raw_securities_pkey CASCADE;
            ALTER TABLE raw_securities ADD PRIMARY KEY (symbol);
        """)
        print("Successfully made 'symbol' the Primary Key of raw_securities.")

        print("\n2. Preparing raw_price_history for Foreign Key (One-to-Many)...")
        # Find any symbols in raw_price_history that don't exist in raw_securities
        cur.execute("""
            SELECT DISTINCT "symbol" FROM raw_price_history 
            WHERE "symbol" NOT IN (SELECT symbol FROM raw_securities);
        """)
        missing_history = cur.fetchall()
        if missing_history:
            print(f"Found missing symbols in raw_price_history: {[row[0] for row in missing_history]}")
            placeholder_id = -1
            for row in missing_history:
                sym = row[0]
                cur.execute("""
                    INSERT INTO raw_securities (id, symbol, security_name, name, active_status)
                    VALUES (%s, %s, %s, %s, 'A') ON CONFLICT DO NOTHING;
                """, (placeholder_id, sym, sym, sym))
                placeholder_id -= 1
            print("Inserted missing symbols into raw_securities as placeholders.")

        # Now add the foreign key
        try:
            cur.execute("""
                ALTER TABLE raw_price_history DROP CONSTRAINT IF EXISTS fk_price_history_symbol;
                ALTER TABLE raw_price_history ADD CONSTRAINT fk_price_history_symbol 
                FOREIGN KEY ("symbol") REFERENCES raw_securities(symbol);
            """)
            print("Successfully added Foreign Key to raw_price_history (One-to-Many).")
        except Exception as e:
            print(f"Failed to add FK to raw_price_history: {e}")

        print("\n3. Preparing raw_mf_sharesansar_nav for Foreign Key (One-to-One)...")
        # Ensure no missing symbols
        cur.execute("""
            SELECT DISTINCT "symbol" FROM raw_mf_sharesansar_nav 
            WHERE "symbol" NOT IN (SELECT symbol FROM raw_securities);
        """)
        missing_mf = cur.fetchall()
        if missing_mf:
            print(f"Found missing symbols in raw_mf_sharesansar_nav: {[row[0] for row in missing_mf]}")
            placeholder_id = -100
            for row in missing_mf:
                sym = row[0]
                cur.execute("""
                    INSERT INTO raw_securities (id, symbol, security_name, name, active_status)
                    VALUES (%s, %s, %s, %s, 'A') ON CONFLICT DO NOTHING;
                """, (placeholder_id, sym, sym, sym))
                placeholder_id -= 1
            print("Inserted missing MF symbols into raw_securities as placeholders.")

        # Add the foreign key
        try:
            cur.execute("""
                ALTER TABLE raw_mf_sharesansar_nav DROP CONSTRAINT IF EXISTS fk_mf_nav_symbol;
                ALTER TABLE raw_mf_sharesansar_nav ADD CONSTRAINT fk_mf_nav_symbol 
                FOREIGN KEY ("symbol") REFERENCES raw_securities(symbol);
            """)
            print("Successfully added Foreign Key to raw_mf_sharesansar_nav (One-to-One since Symbol is its PK).")
        except Exception as e:
            print(f"Failed to add FK to raw_mf_sharesansar_nav: {e}")

        print("\n4. Confirming raw_nepseapi_live_prices relation (One-to-One)...")
        # Since we added it in setup_price_tables.py, let's just make sure it's valid.
        print("raw_nepseapi_live_prices already has 'symbol' as PK and a Foreign Key to raw_securities(symbol).")
        
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    update_schema()
