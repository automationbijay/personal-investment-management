import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor()

sql = """
DO $$
BEGIN
    -- Drop the old constraint pointing to raw_mf_sharesansar_nav
    IF EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_mf_assets_sharesansar') THEN
        ALTER TABLE public.mf_assets_value_change DROP CONSTRAINT fk_mf_assets_sharesansar;
    END IF;
    
    -- Add the new constraint pointing to the raw_mutual_funds master table
    ALTER TABLE public.mf_assets_value_change ADD CONSTRAINT fk_mf_assets_parent FOREIGN KEY ("MF") REFERENCES public.raw_mutual_funds(symbol) NOT VALID;
END $$;
"""

try:
    cur.execute(sql)
    conn.commit()
    print("Successfully repointed mf_assets_value_change FK to raw_mutual_funds.")
except Exception as e:
    conn.rollback()
    print(f"Error: {e}")
    
cur.close()
conn.close()
