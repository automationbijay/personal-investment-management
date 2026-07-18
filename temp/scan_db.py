import os
import json
import psycopg2
from dotenv import load_dotenv

load_dotenv()
db_url = os.getenv("DATABASE_URL")

conn = psycopg2.connect(db_url)
conn.autocommit = True
cur = conn.cursor()

data = {}

# 1. Get Tables and Row Estimates
cur.execute("""
    SELECT relname, n_live_tup, seq_scan, seq_tup_read, idx_scan, idx_tup_fetch
    FROM pg_stat_user_tables
    WHERE schemaname = 'public'
""")
tables = cur.fetchall()
data['tables'] = [{"table": row[0], "rows": row[1], "seq_scan": row[2], "seq_tup_read": row[3], "idx_scan": row[4], "idx_tup_fetch": row[5]} for row in tables]

# 2. Get Foreign Keys that lack indexes
cur.execute("""
    WITH fk_actions AS (
        SELECT
            conrelid::regclass AS table_name,
            a.attname AS column_name,
            confrelid::regclass AS referenced_table
        FROM pg_constraint c
        JOIN pg_attribute a ON a.attnum = ANY(c.conkey) AND a.attrelid = c.conrelid
        WHERE c.contype = 'f'
    )
    SELECT * FROM fk_actions;
""")
fks = cur.fetchall()
data['foreign_keys'] = [{"table": str(row[0]), "column": row[1], "referenced_table": str(row[2])} for row in fks]

# 3. Get existing indexes
cur.execute("""
    SELECT
        tablename,
        indexname,
        indexdef
    FROM pg_indexes
    WHERE schemaname = 'public';
""")
indexes = cur.fetchall()
data['indexes'] = [{"table": row[0], "index": row[1], "def": row[2]} for row in indexes]

with open('temp/db_scan_results.json', 'w') as f:
    json.dump(data, f, indent=2)

conn.close()
print("Scan complete. Results written to temp/db_scan_results.json")
