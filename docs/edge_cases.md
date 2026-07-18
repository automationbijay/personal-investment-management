# Edge Cases & Troubleshooting

This document tracks known edge cases, weird market scenarios, and specific fallback logic implemented in the database triggers and scripts to keep the data synchronized.

## 1. Mutual Fund Zero-History Fallback (NAV Date Constraint)
**Scenario**: 
A mutual fund portfolio (e.g., from `raw_mf_nepsealpha_assets_lastmonth`) contains a newly listed stock (like `FOWADP`) that started trading *after* the mutual fund's published NAV date. 
For example, the NAV was published on `2026-07-10`, but `FOWADP`'s first trading day was `2026-07-15`.

**The Problem**: 
The `mf_assets_value_change` table has a strict foreign key constraint (`fk_mf_assets_price_history`) linking it directly to `raw_price_history` using `(symbol, weekly_nav_date_actual)`. When the database trigger (`fn_calculate_mf_asset_ltps`) tries to look backwards to find the last traded price prior to `2026-07-10`, it finds absolutely nothing (NULL). This normally results in a foreign key violation, crashing the import.

**The Solution Implemented**:
The `fn_calculate_mf_asset_ltps` trigger includes a specific `ELSIF v_actual_date IS NULL` block. If a stock has completely zero price history prior to the NAV date, the database will dynamically grab the stock's *most recent* (today's) LTP (or `0` if it has never traded at all) and use it to insert a "dummy" fallback row into `raw_price_history` for the exact NAV date. This satisfies the foreign key constraint without breaking the synchronization workflow.

## 2. Trigger Recursion ("tuple already modified" error)
**Scenario**:
When n8n inserts new asset data into `raw_mf_nepsealpha_assets_lastmonth`, it kicks off a chain reaction:
1. `raw_mf_nepsealpha_assets_lastmonth` copies data to `mf_assets_value_change`.
2. `mf_assets_value_change` evaluates prices, and sometimes inserts a missing row into `raw_price_history`.
3. `raw_price_history` normally has a trigger that detects price changes and immediately tries to update `mf_assets_value_change`.

**The Problem**:
Because Step 1 is already in the middle of updating `mf_assets_value_change`, when Step 3 tries to update the exact same tuple again before the transaction is finished, PostgreSQL panics and throws: `"tuple to be updated was already modified by an operation triggered by the current command"`.

**The Solution Implemented**:
We broke the loop by adding `IF pg_trigger_depth() > 1 THEN RETURN NEW; END IF;` to the `fn_update_mf_analytics_on_price_change` trigger. This ensures that if the price change was initiated deeply inside another trigger's transaction (like our fallback row generator), it won't attempt to recursively update the parent table again.

## 3. Auto-Creating Missing Foreign Keys (Unlisted Mutual Funds)
**Scenario**:
When importing mutual fund portfolios (e.g., via `raw_mf_nepsealpha_assets_lastmonth`), the scraper may encounter assets or mutual funds that are unlisted or brand new (e.g., open-ended mutual funds like `ELIS` or `MSY`). 

**The Problem**:
If a symbol does not exist in the master tables (`raw_securities` or `raw_mutual_funds`), PostgreSQL will reject the entire batch insert due to foreign key violations. You cannot use `ON CONFLICT DO NOTHING` for foreign key errors.

**The Solution Implemented**:
A `BEFORE INSERT OR UPDATE` trigger named `trg_auto_create_missing_fks` runs on `raw_mf_nepsealpha_assets_lastmonth`. 
It intercepts the row, checks if the `MF` and `symbol` exist in their respective master tables. If they are missing, it dynamically inserts a placeholder row into `raw_mutual_funds` and `raw_securities` with the `source` column set to `'auto-placeholder-nepsealpha'`. This instantly resolves the foreign key violation on the fly, allowing the import to proceed without dropping valuable portfolio data.
