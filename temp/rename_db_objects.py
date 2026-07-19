import os
import psycopg2
from dotenv import load_dotenv

def migrate():
    load_dotenv()
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("DATABASE_URL not found in .env")
        return

    conn = psycopg2.connect(db_url)
    conn.autocommit = True
    cur = conn.cursor()

    commands = [
        # Rename the average table if it exists
        "ALTER TABLE IF EXISTS public.average RENAME TO wiki_average;",
        
        # Rename views (assuming they exist, use IF EXISTS to avoid errors)
        "ALTER VIEW IF EXISTS public.vw_mf_summary_analytics RENAME TO view_mf_summary_analytics;",
        "ALTER VIEW IF EXISTS public.mf_assets_value_change RENAME TO view_mf_assets_value_change;",
        "ALTER VIEW IF EXISTS public.mf_ask_bid RENAME TO view_mf_ask_bid;",
        "ALTER VIEW IF EXISTS public.deb_ytm_analysis RENAME TO view_deb_ytm_analysis;"
    ]

    for cmd in commands:
        try:
            cur.execute(cmd)
            print(f"Executed: {cmd}")
        except Exception as e:
            print(f"Error executing {cmd}: {e}")

    cur.close()
    conn.close()

if __name__ == "__main__":
    migrate()
