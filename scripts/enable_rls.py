import os
import psycopg2
from dotenv import load_dotenv

def enable_rls_on_all_tables():
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
            WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
        """)
        
        tables = cur.fetchall()
        
        for (table_name,) in tables:
            print(f"Processing table: {table_name}")
            
            # Enable RLS
            cur.execute(f'ALTER TABLE "{table_name}" ENABLE ROW LEVEL SECURITY;')
            print(f"  - Enabled RLS")
            
            # Create a policy to allow authenticated users to read (SELECT)
            # We use IF NOT EXISTS to avoid errors if run multiple times, though PG13+ doesn't support IF NOT EXISTS on CREATE POLICY directly.
            # Instead we can drop it first or check if it exists.
            policy_name = f"Enable read access for authenticated users on {table_name}"
            
            cur.execute(f"""
                DO $$
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1
                        FROM pg_policies
                        WHERE schemaname = 'public'
                          AND tablename = '{table_name}'
                          AND policyname = '{policy_name}'
                    ) THEN
                        CREATE POLICY "{policy_name}" ON "{table_name}" 
                        FOR SELECT TO authenticated USING (true);
                    END IF;
                END
                $$;
            """)
            print(f"  - Created/Verified read policy for authenticated users")
            
            # Optionally allow authenticated users to insert/update/delete?
            # Or perhaps just read for now, as per standard safety.
            
        conn.commit()
        cur.close()
        conn.close()
        print("Successfully enabled RLS and applied basic read policies to all tables.")
    except Exception as e:
        print(f"Failed to query database. Error: {e}")

if __name__ == "__main__":
    enable_rls_on_all_tables()
