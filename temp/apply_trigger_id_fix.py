import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
db_url = os.getenv('DATABASE_URL')

if not db_url:
    print('No DATABASE_URL found.')
    exit(1)

sql = """
CREATE OR REPLACE FUNCTION trg_insert_missing_security()
RETURNS TRIGGER AS $$
DECLARE
    next_id integer;
BEGIN
    -- Check if the symbol is missing in the parent table
    IF NOT EXISTS (SELECT 1 FROM raw_securities WHERE symbol = NEW.symbol) THEN
        -- Get the max id to prevent null violation
        SELECT COALESCE(MAX(id), 0) + 1 INTO next_id FROM raw_securities;
        
        -- Insert a placeholder record to satisfy the foreign key
        INSERT INTO raw_securities (id, symbol, security_name, name, source)
        VALUES (next_id, NEW.symbol, NEW.symbol, NEW.symbol, 'meroshare_auto_insert');
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
"""

try:
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()
    cur.execute(sql)
    conn.commit()
    print('Successfully updated trigger function to handle missing id.')
    cur.close()
    conn.close()
except Exception as e:
    print('Error applying migration:', e)
