import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
db_url = os.environ.get("DATABASE_URL")
if not db_url:
    print("DATABASE_URL not found")
    exit(1)

conn = psycopg2.connect(db_url)
conn.autocommit = True
cur = conn.cursor()

def fetch_and_write(title, query, f):
    f.write(f"\n--- {title} ---\n")
    cur.execute(query)
    columns = [desc[0] for desc in cur.description] if cur.description else []
    rows = cur.fetchall()
    f.write(", ".join(columns) + "\n")
    for row in rows:
        f.write(str(row) + "\n")

with open("temp/schema_dump.txt", "w", encoding="utf-8") as f:
    # 1. Tables and Views
    fetch_and_write("TABLES AND VIEWS", """
        SELECT table_name, table_type 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        ORDER BY table_name;
    """, f)
    
    # 2. Columns (to check for missing FK indexes, etc)
    fetch_and_write("COLUMNS", """
        SELECT table_name, column_name, data_type, is_nullable, column_default 
        FROM information_schema.columns 
        WHERE table_schema = 'public'
        ORDER BY table_name, ordinal_position;
    """, f)
    
    # 3. Primary, Foreign Keys, Unique constraints
    fetch_and_write("CONSTRAINTS (FK, PK, UNIQUE)", """
        SELECT 
            tc.table_name, 
            kcu.column_name, 
            tc.constraint_type, 
            ccu.table_name AS foreign_table_name, 
            ccu.column_name AS foreign_column_name 
        FROM information_schema.table_constraints tc 
        JOIN information_schema.key_column_usage kcu 
          ON tc.constraint_name = kcu.constraint_name 
          AND tc.table_schema = kcu.table_schema 
        JOIN information_schema.constraint_column_usage ccu 
          ON ccu.constraint_name = tc.constraint_name 
          AND ccu.table_schema = tc.table_schema 
        WHERE tc.table_schema = 'public'
        ORDER BY tc.table_name;
    """, f)
    
    # 4. Indexes (to check for redundant or missing FK indexes)
    fetch_and_write("INDEXES", """
        SELECT tablename, indexname, indexdef 
        FROM pg_indexes 
        WHERE schemaname = 'public' 
        ORDER BY tablename, indexname;
    """, f)
    
    # 5. Functions
    fetch_and_write("FUNCTIONS", """
        SELECT p.proname AS function_name, 
               pg_get_function_arguments(p.oid) AS arguments, 
               pg_get_function_result(p.oid) AS return_type, 
               CASE WHEN p.prosecdef THEN 'SECURITY DEFINER' ELSE 'SECURITY INVOKER' END as security_type,
               p.prosrc AS body
        FROM pg_proc p 
        JOIN pg_namespace n ON n.oid = p.pronamespace 
        WHERE n.nspname = 'public'
        ORDER BY function_name;
    """, f)
    
    # 6. Triggers
    fetch_and_write("TRIGGERS", """
        SELECT event_object_table AS table_name, 
               trigger_name, 
               event_manipulation AS event, 
               action_timing AS timing, 
               action_statement AS statement 
        FROM information_schema.triggers 
        WHERE event_object_schema = 'public' 
        ORDER BY table_name, trigger_name;
    """, f)

    # 7. RLS Policies
    fetch_and_write("RLS POLICIES", """
        SELECT tablename, policyname, permissive, roles, cmd, qual, with_check 
        FROM pg_policies 
        WHERE schemaname = 'public' 
        ORDER BY tablename, policyname;
    """, f)

    # 8. RLS Enabled tables
    fetch_and_write("RLS ENABLED TABLES", """
        SELECT relname, relrowsecurity 
        FROM pg_class 
        WHERE relnamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'public') 
          AND relkind = 'r' 
        ORDER BY relname;
    """, f)
    
    # 9. Views (Security Invoker vs Definer)
    fetch_and_write("VIEWS OPTIONS", """
        SELECT c.relname as view_name, c.reloptions
        FROM pg_class c
        JOIN pg_namespace n ON n.oid = c.relnamespace
        WHERE n.nspname = 'public' AND c.relkind = 'v';
    """, f)

cur.close()
conn.close()
print("Dumped schema to temp/schema_dump.txt")
