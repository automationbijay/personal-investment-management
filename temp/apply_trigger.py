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
BEGIN
    -- Check if the symbol is missing in the parent table
    IF NOT EXISTS (SELECT 1 FROM raw_securities WHERE symbol = NEW.symbol) THEN
        -- Insert a placeholder record to satisfy the foreign key
        INSERT INTO raw_securities (symbol, security_name, name, source)
        VALUES (NEW.symbol, NEW.symbol, NEW.symbol, 'meroshare_auto_insert');
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_ensure_security_exists ON raw_meroshare_portfolio;

CREATE TRIGGER trg_ensure_security_exists
BEFORE INSERT OR UPDATE ON raw_meroshare_portfolio
FOR EACH ROW
EXECUTE FUNCTION trg_insert_missing_security();
"""

try:
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()
    cur.execute(sql)
    conn.commit()
    print('Successfully applied trigger and function to auto-insert missing symbols.')
    cur.close()
    conn.close()
except Exception as e:
    print('Error applying migration:', e)
