import os, psycopg2
from dotenv import load_dotenv

load_dotenv()
try:
    conn = psycopg2.connect(os.getenv('DATABASE_URL'))
    conn.autocommit = True
    cur = conn.cursor()
    
    # Drop the obsolete trigger
    cur.execute('DROP TRIGGER IF EXISTS trg_sync_analytics_on_raw_change ON public.raw_mf_nepsealpha_assets_lastmonth CASCADE;')
    print('Dropped trigger trg_sync_analytics_on_raw_change')
    
    # Drop the obsolete function
    cur.execute('DROP FUNCTION IF EXISTS public.fn_sync_analytics_from_raw() CASCADE;')
    print('Dropped function fn_sync_analytics_from_raw')
    
except Exception as e:
    print("Error:", e)
