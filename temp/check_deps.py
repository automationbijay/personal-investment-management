import os
import psycopg2
from dotenv import load_dotenv

def main():
    load_dotenv()
    conn = psycopg2.connect(os.getenv('DATABASE_URL'))
    cur = conn.cursor()
    
    cur.execute("SELECT v.viewname, pg_get_viewdef(v.viewname) FROM pg_views v WHERE v.schemaname = 'public';")
    print("--- VIEWS ---")
    for row in cur.fetchall():
        if 'raw_nepseapi_live_prices' in row[1]:
            print(row[0])
            
    print("--- FUNCTIONS/PROCEDURES ---")
    cur.execute("SELECT proname, prosrc FROM pg_proc JOIN pg_namespace ON pg_namespace.oid = pg_proc.pronamespace WHERE nspname = 'public';")
    for row in cur.fetchall():
        if row[1] and 'raw_nepseapi_live_prices' in row[1]:
            print(row[0])

if __name__ == '__main__':
    main()
