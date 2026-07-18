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

report = ["# Database Audit Report", ""]

# 1. RLS Enabled Tables
cur.execute("""
    SELECT relname, relrowsecurity 
    FROM pg_class 
    WHERE relnamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'public') 
      AND relkind = 'r' 
    ORDER BY relname;
""")
rls_issues = [row[0] for row in cur.fetchall() if not row[1]]
report.append("## Row Level Security (RLS)")
if rls_issues:
    report.append("> [!WARNING]")
    report.append("> The following tables do not have RLS enabled. This is a security risk if the Data API is exposed.")
    for t in rls_issues:
        report.append(f"- {t}")
else:
    report.append("All tables have RLS enabled.")
report.append("")

# 2. Missing Foreign Key Indexes
cur.execute("""
    WITH fk_actions AS (
      SELECT conname, conrelid, confrelid,
             unnest(conkey) AS column_index
      FROM pg_constraint
      WHERE contype = 'f'
    ),
    fk_columns AS (
      SELECT f.conname, c.relname AS table_name, a.attname AS column_name
      FROM fk_actions f
      JOIN pg_class c ON c.oid = f.conrelid
      JOIN pg_attribute a ON a.attrelid = f.conrelid AND a.attnum = f.column_index
    ),
    indexed_columns AS (
      SELECT c.relname AS table_name, a.attname AS column_name
      FROM pg_index i
      JOIN pg_class c ON c.oid = i.indrelid
      JOIN pg_attribute a ON a.attrelid = i.indrelid AND a.attnum = ANY(i.indkey)
    )
    SELECT f.table_name, f.column_name
    FROM fk_columns f
    JOIN pg_class c ON c.relname = f.table_name
    JOIN pg_namespace n ON n.oid = c.relnamespace
    LEFT JOIN indexed_columns i ON f.table_name = i.table_name AND f.column_name = i.column_name
    WHERE i.column_name IS NULL AND n.nspname = 'public';
""")
missing_fk_indexes = cur.fetchall()
report.append("## Missing Foreign Key Indexes")
if missing_fk_indexes:
    report.append("> [!TIP]")
    report.append("> Adding indexes to foreign key columns can significantly improve query performance, especially for cascading deletes and joins.")
    for table, col in set(missing_fk_indexes):
        report.append(f"- Table `{table}`, Column `{col}`")
else:
    report.append("All foreign keys are indexed.")
report.append("")

# 3. Views Without Security Invoker
cur.execute("""
    SELECT c.relname as view_name, c.reloptions
    FROM pg_class c
    JOIN pg_namespace n ON n.oid = c.relnamespace
    WHERE n.nspname = 'public' AND c.relkind = 'v';
""")
views = cur.fetchall()
report.append("## Views Security")
invoker_missing = []
for view, options in views:
    if options is None or 'security_invoker=true' not in options:
        invoker_missing.append(view)
if invoker_missing:
    report.append("> [!WARNING]")
    report.append("> The following views do not have `security_invoker = true`. They will bypass RLS.")
    for v in invoker_missing:
        report.append(f"- {v}")
else:
    report.append("All views have security_invoker = true.")
report.append("")

# 4. Security Definer Functions
cur.execute("""
    SELECT p.proname AS function_name
    FROM pg_proc p 
    JOIN pg_namespace n ON n.oid = p.pronamespace 
    WHERE n.nspname = 'public' AND p.prosecdef;
""")
definer_funcs = cur.fetchall()
report.append("## Security Definer Functions")
if definer_funcs:
    report.append("> [!CAUTION]")
    report.append("> The following functions are `SECURITY DEFINER` in the `public` schema. They run with elevated privileges and can be called by anyone.")
    for f in definer_funcs:
        report.append(f"- {f[0]}")
else:
    report.append("No SECURITY DEFINER functions found in public schema.")
report.append("")

# 5. Redundant Indexes
cur.execute("""
    WITH pk_indexes AS (
        SELECT i.indexrelid
        FROM pg_index i
        WHERE i.indisprimary
    )
    SELECT
        c.relname AS table_name,
        i.relname AS index_name,
        pg_get_indexdef(i.oid) AS index_def
    FROM pg_index idx
    JOIN pg_class i ON i.oid = idx.indexrelid
    JOIN pg_class c ON c.oid = idx.indrelid
    JOIN pg_namespace n ON c.relnamespace = n.oid
    WHERE n.nspname = 'public'
      AND idx.indexrelid NOT IN (SELECT indexrelid FROM pk_indexes)
      AND idx.indisunique; -- Many redundant user created indexes are unique but pk is already unique. We should inspect all to be safe but filtering unique for simplicity.
""")
# Simple redundant index check is hard in pure query without pg_stat, but we list user indexes for review.
cur.execute("""
    SELECT tablename, indexname, indexdef
    FROM pg_indexes
    WHERE schemaname = 'public'
""")
indexes = cur.fetchall()
report.append("## Custom Indexes (Check for redundancy)")
report.append("Review these indexes. If they duplicate primary key indexes, they should be removed per `AGENTS.md` rules.")
for t, i, d in indexes:
    if not i.endswith("_pkey"):
        report.append(f"- Table `{t}`, Index `{i}`: `{d}`")
report.append("")

with open("temp/audit_report.md", "w", encoding="utf-8") as f:
    f.write("\n".join(report))

print("Audit report generated at temp/audit_report.md")
