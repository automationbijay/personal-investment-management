import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
db_url = os.getenv("DATABASE_URL")
conn = psycopg2.connect(db_url)
cur = conn.cursor()

# 1. Create the new table
create_table_sql = """
CREATE TABLE IF NOT EXISTS public.wiki_profit_loss_analysis (
    symbol TEXT PRIMARY KEY,
    quantity NUMERIC,
    wacc_rate NUMERIC,
    total_investment NUMERIC,
    live_ltp NUMERIC,
    current_value NUMERIC,
    overall_profit_loss_amount NUMERIC,
    overall_profit_loss_percent NUMERIC,
    daily_change_per_share NUMERIC,
    daily_gain_loss_amount NUMERIC,
    daily_gain_loss_percent NUMERIC,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
"""
cur.execute(create_table_sql)

# Enable RLS
rls_sql = """
ALTER TABLE public.wiki_profit_loss_analysis ENABLE ROW LEVEL SECURITY;
"""
cur.execute(rls_sql)

conn.commit()
print("Table wiki_profit_loss_analysis created successfully.")

cur.close()
conn.close()
