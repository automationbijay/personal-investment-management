import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
db_url = os.getenv('DATABASE_URL')

if db_url:
    try:
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        
        tables = [
            'raw_deb_nepsealpha_details',
            'raw_deb_nepseapi_marketdepth',
            'raw_meroshare_portfolio',
            'raw_meroshare_wacc',
            'raw_mf_nepsealpha_assets_allocation',
            'raw_mf_nepsealpha_assets_lastmonth',
            'raw_mf_nepsealpha_details',
            'raw_mf_sharesansar_nav',
            'raw_mutual_funds',
            'raw_nepseapi_live_prices',
            'raw_price_history',
            'raw_securities'
        ]
        
        for table in tables:
            cur.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = %s AND column_name = 'updated_at';
            """, (table,))
            result = cur.fetchone()
            has_column = result is not None
            print(f"{table}: has_updated_at={has_column}")
        
        cur.close()
        conn.close()
    except Exception as e:
        print('Error:', e)
