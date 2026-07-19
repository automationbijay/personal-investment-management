# Edge Cases & Troubleshooting

This document tracks known edge cases, weird market scenarios, and specific fallback logic implemented in the database triggers and scripts to keep the data synchronized.

## 1. Mutual Fund Zero-History Fallback (NAV Date Constraint) [DEPRECATED]
**Note**: *This section applies to the legacy trigger-based architecture. `view_mf_assets_value_change` is now a dynamically generated `VIEW`, eliminating these foreign key constraint issues entirely.*

**Scenario**: 
A mutual fund portfolio (e.g., from `raw_mf_nepsealpha_assets_lastmonth`) contains a newly listed stock (like `FOWADP`) that started trading *after* the mutual fund's published NAV date. 

**The Legacy Problem**: 
The old physical `view_mf_assets_value_change` table had a strict foreign key constraint (`fk_mf_assets_price_history`). When a trigger tried to look backwards to find the last traded price, it found nothing (NULL), crashing the import. This was solved by dynamically inserting "dummy" fallback rows into `raw_price_history`. Now, the dynamic view simply uses `LEFT JOIN` on dates, safely rendering missing historical dates as `NULL` without crashing.

## 2. Trigger Recursion ("tuple already modified" error) [DEPRECATED]
**Note**: *This section applies to the legacy trigger-based architecture. Since analytics are now processed dynamically via views, this trigger recursion loop no longer exists.*

**Scenario**:
When n8n inserted new asset data, it kicked off a chain reaction copying data between multiple tables and triggering price history updates, which sometimes recursively triggered updates back onto the parent table, causing PostgreSQL to throw a `"tuple to be updated was already modified by an operation triggered by the current command"` error. This was formerly solved by using `pg_trigger_depth()`.

## 3. Auto-Creating Missing Foreign Keys (Unlisted Mutual Funds)
**Scenario**:
When importing mutual fund portfolios (e.g., via `raw_mf_nepsealpha_assets_lastmonth`), the scraper may encounter assets or mutual funds that are unlisted or brand new (e.g., open-ended mutual funds like `ELIS` or `MSY`). 

**The Problem**:
If a symbol does not exist in the master tables (`raw_securities` or `raw_mutual_funds`), PostgreSQL will reject the entire batch insert due to foreign key violations. You cannot use `ON CONFLICT DO NOTHING` for foreign key errors.

**The Solution Implemented**:
A `BEFORE INSERT OR UPDATE` trigger named `trg_auto_create_missing_fks` runs on `raw_mf_nepsealpha_assets_lastmonth`. 
It intercepts the row, checks if the `MF` and `symbol` exist in their respective master tables. If they are missing, it dynamically inserts a placeholder row into `raw_mutual_funds` and `raw_securities` with the `source` column set to `'auto-placeholder-nepsealpha'`. This instantly resolves the foreign key violation on the fly, allowing the import to proceed without dropping valuable portfolio data.
