import os
import psycopg2
import csv
from dotenv import load_dotenv
from io import StringIO

load_dotenv()

# Read the CSV file
csv_path = 'Mutual Fund Nepsealpha_rows.csv'

conn = psycopg2.connect(os.environ['DATABASE_URL'])
conn.autocommit = True
cur = conn.cursor()

# Create table
create_table_sql = """
CREATE TABLE IF NOT EXISTS raw_mf_nepsealpha_details (
    symbol TEXT PRIMARY KEY REFERENCES raw_mutual_funds(symbol) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()),
    name TEXT,
    type TEXT,
    total_paid_up TEXT,
    date_of_maturity DATE,
    time_to_mature TEXT,
    monthly_nav NUMERIC,
    ltp_vs_weekly_nav NUMERIC,
    weekly_nav NUMERIC,
    ltp NUMERIC,
    weekly_nav_date_bs TEXT,
    weekly_nav_date_ad DATE,
    monthly_nav_date TEXT
);
"""

cur.execute(create_table_sql)
print("Table raw_mf_nepsealpha_details created.")

# Parse CSV and Insert
with open(csv_path, 'r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    for row in reader:
        symbol = row['Symbol']
        name = row['Name']
        mf_type = row['TYPE']
        total_paid_up = row['Total Paid Up'].replace(',', '') if row['Total Paid Up'] else None
        date_of_maturity = row['Date of Maturity'] if row['Date of Maturity'] else None
        time_to_mature = row['Time to Mature'] if row['Time to Mature'] else None
        monthly_nav = float(row['Monthly Nav']) if row['Monthly Nav'] and row['Monthly Nav'] != '-' else None
        ltp_vs_weekly_nav = float(row['LTP Vs Weekly NAV']) if row['LTP Vs Weekly NAV'] and row['LTP Vs Weekly NAV'] != '-' else None
        weekly_nav = float(row['Weekly NAV (Rs.)']) if row['Weekly NAV (Rs.)'] and row['Weekly NAV (Rs.)'] != '-' else None
        ltp = float(row['LTP (Rs.)']) if row['LTP (Rs.)'] and row['LTP (Rs.)'] != '-' else None
        weekly_nav_date = row['weekly nav date'] if row['weekly nav date'] else None
        weekly_nav_ad = row['weekly nav AD'] if row['weekly nav AD'] else None
        monthly_nav_date = row['monthly nav date'] if row['monthly nav date'] else None
        
        # Insert or update
        insert_sql = """
        INSERT INTO raw_mf_nepsealpha_details (
            symbol, name, type, total_paid_up, date_of_maturity, time_to_mature,
            monthly_nav, ltp_vs_weekly_nav, weekly_nav, ltp,
            weekly_nav_date_bs, weekly_nav_date_ad, monthly_nav_date
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
        ON CONFLICT (symbol) DO UPDATE SET
            name = EXCLUDED.name,
            type = EXCLUDED.type,
            total_paid_up = EXCLUDED.total_paid_up,
            date_of_maturity = EXCLUDED.date_of_maturity,
            time_to_mature = EXCLUDED.time_to_mature,
            monthly_nav = EXCLUDED.monthly_nav,
            ltp_vs_weekly_nav = EXCLUDED.ltp_vs_weekly_nav,
            weekly_nav = EXCLUDED.weekly_nav,
            ltp = EXCLUDED.ltp,
            weekly_nav_date_bs = EXCLUDED.weekly_nav_date_bs,
            weekly_nav_date_ad = EXCLUDED.weekly_nav_date_ad,
            monthly_nav_date = EXCLUDED.monthly_nav_date,
            updated_at = timezone('utc'::text, now())
        """
        try:
            cur.execute(insert_sql, (
                symbol, name, mf_type, total_paid_up, date_of_maturity, time_to_mature,
                monthly_nav, ltp_vs_weekly_nav, weekly_nav, ltp,
                weekly_nav_date, weekly_nav_ad, monthly_nav_date
            ))
        except Exception as e:
            print(f"Error inserting {symbol}: {e}")
            conn.rollback()

print("Data inserted successfully.")
cur.close()
conn.close()
