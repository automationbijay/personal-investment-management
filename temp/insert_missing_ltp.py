import os
import csv
import psycopg2
from dotenv import load_dotenv

def main():
    load_dotenv()
    
    csv_file_path = r"c:\Users\purib\Desktop\investmetn management supabse db\new_ltp_only_rows (3).csv"
    
    # Connect to Supabase DB
    conn = psycopg2.connect(os.getenv('DATABASE_URL'))
    cur = conn.cursor()
    
    # Get existing symbols
    cur.execute('SELECT "symbol" FROM raw_nepseapi_live_prices')
    existing_symbols = {row[0] for row in cur.fetchall() if row[0]}
    
    new_records = []
    
    with open(csv_file_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            symbol = row.get('Script')
            price_str = row.get('Price')
            traded_date = row.get('Traded _date')
            
            if not symbol or symbol.strip() == "" or symbol == "Loading...":
                continue
                
            if symbol in existing_symbols:
                continue
                
            if not price_str or price_str.strip() == "":
                continue
                
            try:
                price = float(price_str)
            except ValueError:
                continue
                
            # If traded_date is missing or invalid, we could use None or skip
            # The schema allows timestamp with time zone.
            t_date = traded_date if traded_date and traded_date.strip() != "" else None
            
            new_records.append((symbol, price, t_date))
            existing_symbols.add(symbol) # avoid duplicates from csv itself
            
    if new_records:
        print(f"Found {len(new_records)} new symbols to insert.")
        
        insert_query = 'INSERT INTO raw_nepseapi_live_prices ("symbol", "LTP", "last_updated_time") VALUES (%s, %s, %s)'
        cur.executemany(insert_query, new_records)
        conn.commit()
        print("Insertion successful!")
    else:
        print("No new symbols to insert.")
        
    cur.close()
    conn.close()

if __name__ == "__main__":
    main()
