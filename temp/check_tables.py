import os
import psycopg2
from dotenv import load_dotenv

def list_tables():
    load_dotenv()
    db_url = os.getenv("DATABASE_URL")
    
    if not db_url:
        print("DATABASE_URL not found in .env")
        return
        
    try:
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        
        # Query to list all tables in the public schema
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        
        tables = cur.fetchall()
        print(f"--- Tables in 'public' schema ---")
        if not tables:
            print("No tables found in public schema.")
        for table in tables:
            print(f"- {table[0]}")
            
            # Get columns for each table
            cur.execute(f"""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_schema = 'public' AND table_name = '{table[0]}'
            """)
            columns = cur.fetchall()
            for col in columns:
                print(f"    {col[0]} ({col[1]})")
                
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Failed to query database. Error: {e}")

if __name__ == "__main__":
    list_tables()
