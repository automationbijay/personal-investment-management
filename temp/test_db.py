import os
import psycopg2
from dotenv import load_dotenv

def test_connection():
    load_dotenv()
    db_url = os.getenv("DATABASE_URL")
    
    if not db_url:
        print("DATABASE_URL not found in .env")
        return
        
    try:
        # Connect to your postgres DB
        conn = psycopg2.connect(db_url)
        
        # Open a cursor to perform database operations
        cur = conn.cursor()
        
        # Execute a command: this creates a new table
        cur.execute("SELECT version();")
        
        # Obtain data
        db_version = cur.fetchone()
        print(f"Successfully connected to the database!")
        print(f"PostgreSQL Version: {db_version[0]}")
        
        # Close communication with the database
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Failed to connect to the database. Error: {e}")

if __name__ == "__main__":
    test_connection()
