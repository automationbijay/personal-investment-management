import os
import csv
import psycopg2
from dotenv import load_dotenv

load_dotenv()
conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor()

csv_file = 'new_companies_rows.csv'

sql = """
INSERT INTO public.raw_securities (id, symbol, security_name, name, active_status)
VALUES (%s, %s, %s, %s, %s)
ON CONFLICT (symbol) DO NOTHING;
"""

success_count = 0
try:
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                cur.execute(sql, (
                    int(row['id']),
                    row['symbol'],
                    row['securityname'],
                    row['companyname'],
                    row['status']
                ))
                if cur.rowcount > 0:
                    success_count += 1
            except psycopg2.errors.UniqueViolation as e:
                # If there's a conflict on ID (not symbol), we can catch it
                conn.rollback()
                print(f"Skipping {row['symbol']} due to ID conflict: {e}")
                # Re-establish transaction block after rollback
                cur.execute("BEGIN;")
            except Exception as e:
                conn.rollback()
                print(f"Error on {row['symbol']}: {e}")
                cur.execute("BEGIN;")
                
    conn.commit()
    print(f"Successfully inserted {success_count} missing companies into raw_securities!")
except Exception as e:
    conn.rollback()
    print(f"Global Error: {e}")
    
cur.close()
conn.close()
