"""
Fetches the master list of all tradable securities from the NEPSE API and upserts them into `raw_securities`.
"""

import os
import requests
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv
from health_logger import log_health

def get_securities():
    # Use CompanyList to get richer info like email, website, sector, etc.
    url = "https://neps.puribijay.com.np/CompanyList"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def sync_db():
    load_dotenv()
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("DATABASE_URL not found in .env")
        return

    print("Fetching securities from API...")
    securities = get_securities()
    print(f"Fetched {len(securities)} securities.")
    
    print("Connecting to database...")
    conn = psycopg2.connect(db_url)
    conn.autocommit = True
    cur = conn.cursor()

    # Create table if not exists (with new rich columns)
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS raw_securities (
        id INTEGER PRIMARY KEY,
        symbol TEXT UNIQUE NOT NULL,
        security_name TEXT NOT NULL,
        name TEXT,
        active_status TEXT,
        company_email TEXT,
        website TEXT,
        sector_name TEXT,
        regulatory_body TEXT,
        instrument_type TEXT,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );
    """
    cur.execute(create_table_sql)
    
    # Insert or update data
    insert_sql = """
    INSERT INTO raw_securities (
        id, symbol, security_name, name, active_status, 
        company_email, website, sector_name, regulatory_body, instrument_type
    )
    VALUES %s
    ON CONFLICT (symbol) DO UPDATE SET
        security_name = EXCLUDED.security_name,
        name = EXCLUDED.name,
        active_status = EXCLUDED.active_status,
        company_email = EXCLUDED.company_email,
        website = EXCLUDED.website,
        sector_name = EXCLUDED.sector_name,
        regulatory_body = EXCLUDED.regulatory_body,
        instrument_type = EXCLUDED.instrument_type,
        updated_at = CURRENT_TIMESTAMP;
    """
    
    values = [
        (
            item.get("id"),
            item.get("symbol"),
            item.get("securityName"),
            item.get("companyName"),  # The API uses companyName instead of name
            item.get("status"),       # The API uses status instead of activeStatus
            item.get("companyEmail"),
            item.get("website"),
            item.get("sectorName"),
            item.get("regulatoryBody"),
            item.get("instrumentType")
        )
        for item in securities
    ]
    
    print("Upserting records into the database...")
    try:
        execute_values(cur, insert_sql, values)
        print(f"Successfully synced {len(values)} securities to the database.")
        log_health(cur, 'raw_securities', 'SUCCESS', source_page_url='https://neps.puribijay.com.np/CompanyList', script_ran_from='local')
    except Exception as e:
        log_health(cur, 'raw_securities', f'FAILED: {e}', source_page_url='https://neps.puribijay.com.np/CompanyList', script_ran_from='local')
        raise e
    
    cur.close()
    conn.close()

if __name__ == "__main__":
    try:
        sync_db()
    except Exception as e:
        print(f"Sync failed: {e}")
