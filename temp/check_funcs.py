import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
conn = psycopg2.connect(os.environ['DATABASE_URL'])
cur = conn.cursor()

def get_function_def(func_name):
    cur.execute("""
    SELECT pg_get_functiondef(p.oid)
    FROM pg_proc p
    JOIN pg_namespace n ON n.oid = p.pronamespace
    WHERE p.proname = %s;
    """, (func_name,))
    row = cur.fetchone()
    if row:
        print(f"--- {func_name} ---")
        print(row[0])
    else:
        print(f"Function {func_name} not found.")

get_function_def('refresh_on_portfolio_update')
get_function_def('trg_insert_missing_security')
get_function_def('fn_sync_wiki_profit_loss')
