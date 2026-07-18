import os
import csv
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv

load_dotenv()
db_url = os.getenv('DATABASE_URL')

if not db_url:
    print('No DATABASE_URL found.')
    exit(1)

csv_file = "Distributable-Dividend-17-07-2026.csv"

def parse_pct(val):
    val = val.replace('%', '').strip()
    try:
        return float(val)
    except ValueError:
        return None

try:
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()
    
    print("Reading CSV data with utf-8-sig...")
    records = []
    # Use utf-8-sig to handle BOM which might cause the first column to be skipped
    with open(csv_file, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            symbol = row.get('Symbol', '').strip()
            name = row.get('Name', '').strip()
            date_till = row.get('Date (Till)', '').strip()
            pct_raw = row.get('Expected Dividend', '')
            pct = parse_pct(pct_raw)
            
            if symbol:
                records.append((symbol, name, date_till, pct))
            else:
                print(f"Skipping row missing symbol: {row}")
    
    if records:
        print(f"Upserting {len(records)} records...")
        insert_query = """
            INSERT INTO raw_mf_nepsealpha_dividends (symbol, name, date_till_bs, expected_dividend_pct)
            VALUES %s
            ON CONFLICT (symbol) DO UPDATE SET
                name = EXCLUDED.name,
                date_till_bs = EXCLUDED.date_till_bs,
                expected_dividend_pct = EXCLUDED.expected_dividend_pct,
                updated_at = NOW();
        """
        execute_values(cur, insert_query, records)
        conn.commit()
        print("Data import successful.")
    else:
        print("No records to insert. Check CSV column names.")
    
    cur.close()
    conn.close()
except Exception as e:
    print('Error:', e)
