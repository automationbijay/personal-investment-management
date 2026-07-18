import os
import csv
import psycopg2
from psycopg2.extras import execute_batch
from dotenv import load_dotenv

def main():
    load_dotenv()
    
    csv_file_path = r"c:\Users\purib\Desktop\investmetn management supabse db\new_ltp_only_rows (3).csv"
    
    conn = psycopg2.connect(os.getenv('DATABASE_URL'))
    cur = conn.cursor()
    
    # 1. Alter table to add new columns if they do not exist
    alter_queries = [
        'ALTER TABLE raw_nepseapi_live_prices ADD COLUMN IF NOT EXISTS "created_at" timestamp with time zone;',
        'ALTER TABLE raw_nepseapi_live_prices ADD COLUMN IF NOT EXISTS "ltp_change_percent" numeric;',
        'ALTER TABLE raw_nepseapi_live_prices ADD COLUMN IF NOT EXISTS "turnover" numeric;',
        'ALTER TABLE raw_nepseapi_live_prices ADD COLUMN IF NOT EXISTS "previous_close" numeric;',
        'ALTER TABLE raw_nepseapi_live_prices ADD COLUMN IF NOT EXISTS "change_in_value" numeric;'
    ]
    
    for query in alter_queries:
        cur.execute(query)
    conn.commit()
    print("Table schema updated successfully.")
    
    # 2. Update existing rows with the new data
    updates = []
    
    with open(csv_file_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            symbol = row.get('Script')
            if not symbol or symbol.strip() == "" or symbol == "Loading...":
                continue
                
            created_at_str = row.get('created_at')
            ltp_change_pct_str = row.get('Ltp change percent')
            turnover_str = row.get('turnover')
            prev_close_str = row.get('previous close')
            change_in_val_str = row.get('change in value')
            
            created_at = created_at_str if created_at_str and created_at_str.strip() else None
            
            def safe_float(val):
                if not val or not val.strip():
                    return None
                try:
                    return float(val)
                except ValueError:
                    return None
            
            updates.append({
                'created_at': created_at,
                'ltp_change_percent': safe_float(ltp_change_pct_str),
                'turnover': safe_float(turnover_str),
                'previous_close': safe_float(prev_close_str),
                'change_in_value': safe_float(change_in_val_str),
                'symbol': symbol
            })
    
    if updates:
        update_query = """
            UPDATE raw_nepseapi_live_prices 
            SET "created_at" = COALESCE(%(created_at)s, "created_at"),
                "ltp_change_percent" = %(ltp_change_percent)s,
                "turnover" = %(turnover)s,
                "previous_close" = %(previous_close)s,
                "change_in_value" = %(change_in_value)s
            WHERE "symbol" = %(symbol)s
        """
        execute_batch(cur, update_query, updates)
        conn.commit()
        print(f"Updated {len(updates)} rows with the new column data.")
    else:
        print("No rows to update.")
        
    cur.close()
    conn.close()

if __name__ == "__main__":
    main()
