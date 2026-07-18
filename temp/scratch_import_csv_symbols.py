import os
import csv
import psycopg2
from dotenv import load_dotenv

load_dotenv()
conn = psycopg2.connect(os.getenv('DATABASE_URL'))
conn.autocommit = True
cur = conn.cursor()

csv_file = r'new_mutualfunds_assets_last_month_rows (1).csv'

unique_mfs = set()
unique_symbols = set()

with open(csv_file, 'r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    for row in reader:
        mf = row.get('MF', '').strip()
        if mf:
            unique_mfs.add(mf)
        
        # Note: the column name is 'Symbol', but dict keys are case sensitive.
        # Let's check headers if 'Symbol' or 'symbol'
        sym = row.get('Symbol', '').strip()
        if not sym and 'symbol' in row:
            sym = row.get('symbol', '').strip()
        if sym:
            unique_symbols.add(sym)

print(f"Found {len(unique_mfs)} unique MFs and {len(unique_symbols)} unique Symbols.")

# Combine both for raw_securities
all_securities = unique_mfs.union(unique_symbols)

sql_sec = """
INSERT INTO public.raw_securities (id, symbol, security_name, name, active_status)
VALUES (
    (SELECT COALESCE(MAX(id), 0) + 1 FROM public.raw_securities),
    %s,
    %s,
    %s,
    'A'
) ON CONFLICT (symbol) DO NOTHING;
"""

sec_count = 0
for sym in all_securities:
    # Use symbol name for name as well, since we don't have full names
    cur.execute(sql_sec, (sym, f"{sym} (Auto-added)", f"{sym} (Auto-added)"))
    if cur.rowcount > 0:
        sec_count += 1

print(f"Added {sec_count} new symbols to raw_securities.")

sql_mf = """
INSERT INTO public.raw_mutual_funds (symbol, mutual_fund_name)
VALUES (%s, %s)
ON CONFLICT (symbol) DO NOTHING;
"""

mf_count = 0
for mf in unique_mfs:
    cur.execute(sql_mf, (mf, f"{mf} (Auto-added)"))
    if cur.rowcount > 0:
        mf_count += 1

print(f"Added {mf_count} new MFs to raw_mutual_funds.")

cur.close()
conn.close()
