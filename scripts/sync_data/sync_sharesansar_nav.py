"""
Scrapes weekly mutual fund NAV data from ShareSansar and upserts it into `raw_mf_sharesansar_nav`.
"""

import os
import requests
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv
from health_logger import log_health

def clean_numeric(val):
    if val is None or val == '':
        return None
    try:
        if isinstance(val, str):
            val = val.replace(',', '')
        return float(val)
    except (ValueError, TypeError):
        return None

def convert_date(val):
    if val is None or val == '':
        return None
    # If the date is YYYY-MM-DD, convert to MM/DD/YYYY
    parts = val.split('-')
    if len(parts) == 3 and len(parts[0]) == 4:
        return f"{parts[1]}/{parts[2]}/{parts[0]}"
    return val

def fetch_data():
    url = 'https://www.sharesansar.com/mutual-fund-navs'
    headers = {
        'X-Requested-With': 'XMLHttpRequest',
        'User-Agent': 'Mozilla/5.0'
    }
    
    all_data = []
    start = 0
    length = 50
    
    print("Fetching data from ShareSansar...")
    while True:
        params = {
            'draw': 1,
            'start': start,
            'length': length
        }
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        
        if 'data' not in data or not data['data']:
            break
            
        all_data.extend(data['data'])
        
        # Check if we fetched all records
        if len(all_data) >= data.get('recordsTotal', 0):
            break
            
        start += length
        
    return all_data

def sync_db():
    load_dotenv()
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("DATABASE_URL not found in .env")
        return

    records = fetch_data()
    print(f"Fetched {len(records)} mutual fund records.")

    conn = psycopg2.connect(db_url)
    conn.autocommit = True
    cur = conn.cursor()

    insert_sql = """
    INSERT INTO raw_mf_sharesansar_nav (
        "symbol", 
        "Monthly_Nav", 
        "Weekly_Nav", 
        "LTP", 
        "Fund_Size", 
        "Premium_Discount_Pct", 
        "As_Of", 
        "Weekly_Nav_Date", 
        "Mutual_Fund_Name", 
        "Maturity_Date", 
        "Maturity_Period", 
        "Monthly_Nav_Date"
    )
    VALUES %s
    ON CONFLICT ("symbol") DO UPDATE SET
        "Monthly_Nav" = EXCLUDED."Monthly_Nav",
        "Weekly_Nav" = EXCLUDED."Weekly_Nav",
        "LTP" = EXCLUDED."LTP",
        "Fund_Size" = EXCLUDED."Fund_Size",
        "Premium_Discount_Pct" = EXCLUDED."Premium_Discount_Pct",
        "As_Of" = EXCLUDED."As_Of",
        "Weekly_Nav_Date" = EXCLUDED."Weekly_Nav_Date",
        "Mutual_Fund_Name" = EXCLUDED."Mutual_Fund_Name",
        "Maturity_Date" = EXCLUDED."Maturity_Date",
        "Maturity_Period" = EXCLUDED."Maturity_Period",
        "Monthly_Nav_Date" = EXCLUDED."Monthly_Nav_Date",
        "updated_at" = CURRENT_TIMESTAMP;
    """

    values = []
    for item in records:
        symbol = item.get("symbol")
        if not symbol:
            continue
            
        monthly_nav = clean_numeric(item.get("monthly_nav_price"))
        weekly_nav = clean_numeric(item.get("weekly_nav_price"))
        ltp = clean_numeric(item.get("close"))
        fund_size = clean_numeric(item.get("fund_size"))
        prem_dis = clean_numeric(item.get("prem_dis"))
        
        as_of = convert_date(item.get("published_date") or item.get("daily_date"))
        weekly_date = convert_date(item.get("weekly_date"))
        mf_name = item.get("companyname")
        mat_date = convert_date(item.get("maturity_date"))
        mat_period = item.get("maturity_period")
        monthly_date = item.get("monthly_date")

        values.append((
            symbol,
            monthly_nav,
            weekly_nav,
            ltp,
            fund_size,
            prem_dis,
            as_of,
            weekly_date,
            mf_name,
            mat_date,
            mat_period,
            monthly_date
        ))

    print("Upserting records into the database...")
    try:
        execute_values(cur, insert_sql, values)
        print(f"Successfully synced {len(values)} mutual fund NAVs to the database.")
        log_health(cur, 'raw_mf_sharesansar_nav', 'SUCCESS', source_page_url='https://www.sharesansar.com/mutual-fund-navs', script_ran_from='local')
    except Exception as e:
        log_health(cur, 'raw_mf_sharesansar_nav', f'FAILED: {e}', source_page_url='https://www.sharesansar.com/mutual-fund-navs', script_ran_from='local')
        raise e
    
    cur.close()
    conn.close()

if __name__ == "__main__":
    try:
        sync_db()
    except Exception as e:
        print(f"Sync failed: {e}")
