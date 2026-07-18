import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
conn = psycopg2.connect(os.environ['DATABASE_URL'])
cur = conn.cursor()
conn.autocommit = True

table_name = "raw_mf_nepsealpha_details"
try:
    cur.execute(f"ALTER TABLE {table_name} ENABLE ROW LEVEL SECURITY;")
    cur.execute(f"DROP POLICY IF EXISTS \"Enable read access for all users\" ON {table_name};")
    cur.execute(f"CREATE POLICY \"Enable read access for all users\" ON {table_name} FOR SELECT USING (true);")
    cur.execute(f"DROP POLICY IF EXISTS \"Enable insert for authenticated users only\" ON {table_name};")
    cur.execute(f"CREATE POLICY \"Enable insert for authenticated users only\" ON {table_name} FOR INSERT WITH CHECK (auth.role() = 'authenticated');")
    cur.execute(f"DROP POLICY IF EXISTS \"Enable update for authenticated users only\" ON {table_name};")
    cur.execute(f"CREATE POLICY \"Enable update for authenticated users only\" ON {table_name} FOR UPDATE USING (auth.role() = 'authenticated') WITH CHECK (auth.role() = 'authenticated');")
    print("RLS enabled for raw_mf_nepsealpha_details")
except Exception as e:
    print(f"Error: {e}")

cur.close()
conn.close()
