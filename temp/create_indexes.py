import os
import psycopg2
from dotenv import load_dotenv

def create_indexes():
    load_dotenv()
    db_url = os.getenv("DATABASE_URL")
    
    if not db_url:
        print("DATABASE_URL not found in .env")
        return
        
    try:
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        
        # Define table and columns to index
        indexes_to_create = {
            "raw_price_history": ["symbol", "Date"],
            "mf_assets_value_change": ["symbol", "MF", "Month"],
            "raw_mf_nepsealpha_assets_lastmonth": ["symbol", "MF", "Month"],
            "mf_assets_analytics": ["symbol", "Month"],
            "raw_deb_nepseapi_marketdepth": ["symbol"],
            "raw_mf_sharesansar_nav": ["symbol"],
            "raw_mf_nepsealpha_assets_allocation": ["symbol"],
            "raw_deb_nepsealpha_details": ["symbol"],
            "raw_meroshare_portfolio": ["symbol"],
            "raw_meroshare_wacc": ["symbol"],
            "fundamental_data": ["symbol", "date"],
            "raw_nepseapi_live_prices": ["symbol"],
            "raw_securities": ["symbol"]
        }
        
        for table, columns in indexes_to_create.items():
            for col in columns:
                # generate index name
                idx_name = f"idx_{table}_{col.replace(' ', '_').lower()}"
                
                query = f'CREATE INDEX IF NOT EXISTS "{idx_name}" ON "{table}" ("{col}");'
                print(f"Executing: {query}")
                try:
                    cur.execute(query)
                except Exception as e:
                    print(f"Error creating index on {table}({col}): {e}")
                    conn.rollback() # Rollback on error so we can continue
                else:
                    conn.commit()
                    
        cur.close()
        conn.close()
        print("Successfully created indexes.")
    except Exception as e:
        print(f"Failed to query database. Error: {e}")

if __name__ == "__main__":
    create_indexes()
