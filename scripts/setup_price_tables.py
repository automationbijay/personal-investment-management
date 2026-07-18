"""
Initial schema setup script that created the `raw_nepseapi_live_prices` table and the `vw_live_vs_history_price` comparison view.
"""

import os
import psycopg2
from dotenv import load_dotenv

def setup_price_tables():
    load_dotenv()
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("DATABASE_URL not found in .env")
        return

    conn = psycopg2.connect(db_url)
    conn.autocommit = True
    cur = conn.cursor()

    try:
        # 1. Create raw_nepseapi_live_prices table
        print("Creating raw_nepseapi_live_prices table...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS raw_nepseapi_live_prices (
                "symbol" TEXT PRIMARY KEY,
                "LTP" NUMERIC,
                last_updated_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT fk_live_prices_symbol FOREIGN KEY ("symbol") REFERENCES raw_securities(symbol)
            );
        """)
        print("Successfully created raw_nepseapi_live_prices.")

        # 2. Add Unique Constraint to raw_price_history (if possible)
        print("Adding UNIQUE constraint to raw_price_history...")
        try:
            cur.execute("""
                ALTER TABLE raw_price_history 
                ADD CONSTRAINT unique_symbol_date UNIQUE ("symbol", "Date");
            """)
            print("Successfully added UNIQUE constraint to raw_price_history.")
        except psycopg2.errors.DuplicateTable:
            print("UNIQUE constraint unique_symbol_date already exists.")
        except Exception as e:
            print(f"Could not add UNIQUE constraint (might be duplicates or already exists): {e}")

        # 3. Add Foreign Key to raw_price_history
        print("Adding Foreign Key to raw_price_history...")
        try:
            cur.execute("""
                ALTER TABLE raw_price_history 
                ADD CONSTRAINT fk_price_history_symbol FOREIGN KEY ("symbol") REFERENCES raw_securities(symbol);
            """)
            print("Successfully added Foreign Key to raw_price_history.")
        except psycopg2.errors.DuplicateObject:
            print("Foreign Key fk_price_history_symbol already exists.")
        except Exception as e:
            print(f"Could not add Foreign Key (might have missing symbols in raw_securities): {e}")

        # 4. Create the analytical view
        print("Creating analytical view vw_live_vs_history_price...")
        cur.execute("""
            CREATE OR REPLACE VIEW vw_live_vs_history_price AS
            SELECT 
                l."symbol",
                l."LTP" AS todays_ltp,
                h."Close" AS nav_date_price,
                (l."LTP" - h."Close") AS price_difference,
                h."Date" AS history_date
            FROM raw_nepseapi_live_prices l
            LEFT JOIN raw_price_history h 
                ON l."symbol" = h."symbol";
        """)
        print("Successfully created vw_live_vs_history_price.")

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    setup_price_tables()
