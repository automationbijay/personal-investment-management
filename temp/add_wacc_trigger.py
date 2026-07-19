import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
db_url = os.getenv("DATABASE_URL")
conn = psycopg2.connect(db_url)
cur = conn.cursor()

trigger_sql = """
DROP TRIGGER IF EXISTS trg_sync_pnl_wacc ON public.raw_meroshare_wacc;

CREATE TRIGGER trg_sync_pnl_wacc
AFTER INSERT OR UPDATE ON public.raw_meroshare_wacc
FOR EACH ROW EXECUTE FUNCTION public.fn_sync_wiki_profit_loss();
"""

try:
    cur.execute(trigger_sql)
    conn.commit()
    print("Trigger for raw_meroshare_wacc created successfully!")
except Exception as e:
    conn.rollback()
    print(f"FAILED: {e}")
finally:
    cur.close()
    conn.close()
