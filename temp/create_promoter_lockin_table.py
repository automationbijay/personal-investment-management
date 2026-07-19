import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
db_url = os.environ.get("DATABASE_URL")

sql = """
CREATE TABLE IF NOT EXISTS public.raw_sharesansar_promoter_lockin (
    symbol VARCHAR(50) PRIMARY KEY,
    companyname VARCHAR(255),
    shares NUMERIC,
    prom_share NUMERIC,
    public_share NUMERIC,
    allot_date DATE,
    mf_lock_date DATE,
    prom_lock_date DATE,
    ltp NUMERIC,
    is_locked BOOLEAN,
    as_of_date DATE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Triggers for updated_at and health
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'timestamp_auto' AND tgrelid = 'public.raw_sharesansar_promoter_lockin'::regclass) THEN
        CREATE TRIGGER timestamp_auto
            BEFORE UPDATE ON public.raw_sharesansar_promoter_lockin
            FOR EACH ROW
            EXECUTE FUNCTION public.update_modified_column();
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'health_auto' AND tgrelid = 'public.raw_sharesansar_promoter_lockin'::regclass) THEN
        CREATE TRIGGER health_auto
            AFTER INSERT OR UPDATE ON public.raw_sharesansar_promoter_lockin
            FOR EACH STATEMENT
            EXECUTE FUNCTION public.fn_health_auto();
    END IF;
EXCEPTION
    WHEN undefined_function THEN
        RAISE NOTICE 'Skipping triggers because functions do not exist.';
END $$;

-- Enable RLS
ALTER TABLE public.raw_sharesansar_promoter_lockin ENABLE ROW LEVEL SECURITY;
"""

try:
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()
    cur.execute(sql)
    conn.commit()
    print("Successfully created raw_sharesansar_promoter_lockin table.")
    cur.close()
    conn.close()
except Exception as e:
    print(f"Error: {e}")
