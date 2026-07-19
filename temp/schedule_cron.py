import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
db_url = os.environ.get("DATABASE_URL")
# Use anon key or service role key to invoke edge function
service_role_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

sql = f"""
SELECT cron.schedule(
    'sync_sharesansar_promoter_lockin_job', -- unique job name
    '0 17 */5 * *', -- Every 5 days at 17:00
    $$
    SELECT net.http_post(
        url:='https://isornzmtlnkukfjpemnh.supabase.co/functions/v1/sync_sharesansar_promoter_lockin',
        headers:='{{"Content-Type": "application/json", "Authorization": "Bearer {service_role_key}"}}'::jsonb
    ) as request_id;
    $$
);
"""

try:
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()
    # Unschedule if it exists first
    cur.execute("SELECT cron.unschedule('sync_sharesansar_promoter_lockin_job');")
    conn.commit()
except Exception:
    pass

try:
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()
    cur.execute(sql)
    conn.commit()
    print("Successfully scheduled cron job for sync_sharesansar_promoter_lockin.")
    cur.close()
    conn.close()
except Exception as e:
    print(f"Error: {e}")
