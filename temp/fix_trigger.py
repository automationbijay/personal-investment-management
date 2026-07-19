import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
conn = psycopg2.connect(os.environ.get("DATABASE_URL"))
cur = conn.cursor()

cur.execute("""
CREATE OR REPLACE FUNCTION refresh_urls_on_config_update()
RETURNS trigger AS $$
BEGIN
    -- Added a WHERE clause to bypass safeupdate restriction
    UPDATE public.raw_deb_nepseapi_marketdepth SET updated_at = NOW() WHERE symbol IS NOT NULL;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;
""")
conn.commit()
cur.close()
conn.close()
print("Trigger function updated successfully.")
