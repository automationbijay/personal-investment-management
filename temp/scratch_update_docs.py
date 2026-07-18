import os

file_path = r'c:\Users\purib\Desktop\investmetn management supabse db\docs\edge_cases.md'

content_to_append = """
## 3. Auto-Creating Missing Foreign Keys (Unlisted Mutual Funds)
**Scenario**:
When importing mutual fund portfolios (e.g., via `raw_mf_nepsealpha_assets_lastmonth`), the scraper may encounter assets or mutual funds that are unlisted or brand new (e.g., open-ended mutual funds like `ELIS` or `MSY`). 

**The Problem**:
If a symbol does not exist in the master tables (`raw_securities` or `raw_mutual_funds`), PostgreSQL will reject the entire batch insert due to foreign key violations. You cannot use `ON CONFLICT DO NOTHING` for foreign key errors.

**The Solution Implemented**:
A `BEFORE INSERT OR UPDATE` trigger named `trg_auto_create_missing_fks` runs on `raw_mf_nepsealpha_assets_lastmonth`. 
It intercepts the row, checks if the `MF` and `symbol` exist in their respective master tables. If they are missing, it dynamically inserts a placeholder row into `raw_mutual_funds` and `raw_securities` with the `source` column set to `'auto-placeholder-nepsealpha'`. This instantly resolves the foreign key violation on the fly, allowing the import to proceed without dropping valuable portfolio data.
"""

with open(file_path, 'a', encoding='utf-8') as f:
    f.write(content_to_append)

print("Successfully appended to docs/edge_cases.md")
