import os
import psycopg2
from dotenv import load_dotenv

def create_table():
    load_dotenv()
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("DATABASE_URL not found in .env")
        return

    conn = psycopg2.connect(db_url)
    conn.autocommit = True
    cur = conn.cursor()

    try:
        print("Creating table raw_sharesansar_daily_price...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS public.raw_sharesansar_daily_price (
                symbol TEXT NOT NULL,
                date DATE NOT NULL DEFAULT CURRENT_DATE,
                conf NUMERIC,
                open NUMERIC,
                high NUMERIC,
                low NUMERIC,
                close NUMERIC,
                ltp NUMERIC,
                vwap NUMERIC,
                vol NUMERIC,
                prev_close NUMERIC,
                turnover NUMERIC,
                trans INTEGER,
                diff NUMERIC,
                range NUMERIC,
                diff_percent NUMERIC,
                range_percent NUMERIC,
                vwap_percent NUMERIC,
                days_120 NUMERIC,
                days_180 NUMERIC,
                weeks_52_high NUMERIC,
                weeks_52_low NUMERIC,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                PRIMARY KEY (symbol, date)
            );
        """)

        print("Creating indexes...")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_raw_sharesansar_daily_price_symbol ON public.raw_sharesansar_daily_price(symbol);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_raw_sharesansar_daily_price_date ON public.raw_sharesansar_daily_price(date);")

        print("Attaching health_auto trigger...")
        cur.execute("""
            DO $$ 
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 
                    FROM pg_trigger 
                    WHERE tgname = 'health_auto' 
                    AND tgrelid = 'public.raw_sharesansar_daily_price'::regclass
                ) THEN
                    CREATE TRIGGER health_auto
                    AFTER INSERT OR UPDATE ON public.raw_sharesansar_daily_price
                    FOR EACH STATEMENT
                    EXECUTE FUNCTION public.fn_health_auto();
                END IF;
            END $$;
        """)
        
        print("Table created successfully!")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    create_table()
