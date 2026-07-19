# Database Triggers

To maintain a clean and organized Supabase UI, all database triggers follow a strict categorical naming convention. This ensures they cluster logically when viewing the `information_schema`. 

All triggers in this repository belong to one of the following categories:

## 1. `health_auto`
**Purpose**: Logs synchronization script execution success or failure.
- These triggers fire on any `INSERT` or `UPDATE` on `raw_` data tables.
- They automatically `UPSERT` the latest execution timestamp and status into the `sys_script_health` table.
- **Example Attachments**: `raw_securities`, `raw_nepseapi_live_prices`, `raw_meroshare_portfolio`, etc.

## 2. `timestamp_auto`
**Purpose**: Automatically maintains the `updated_at` column.
- These triggers fire before an `UPDATE` on a row to stamp the exact time the row was modified.
- **Example Attachments**: All tables containing an `updated_at` column.

## 3. `pnl_sync`
**Purpose**: Real-time calculation of Profit and Loss (PnL).
- These triggers fire after a change to holdings, cost basis, or live market prices.
- They execute an efficient UPSERT against the `wiki_profit_loss_analysis` table for the specific stock symbol that changed.
- **Attachments**: `raw_meroshare_portfolio`, `raw_meroshare_wacc`, `raw_nepseapi_live_prices`.

## 4. `analytics_sync`
**Purpose**: Triggers downstream materializations or analytics recalculations.
- Keeps dynamic analysis tables up to date based on raw data changes.
- **Example Attachments**: `raw_price_history` (updates moving averages/analytics).

## 5. `fks_ensure`
**Purpose**: Auto-resolution of foreign key constraints.
- Sometimes data sources provide details for a stock symbol before the symbol officially exists in the `raw_securities` master list.
- These triggers intercept an `INSERT` and automatically create the missing parent record in `raw_securities` to prevent constraint violations.
- **Attachments**: `raw_meroshare_portfolio`, `raw_mf_nepsealpha_assets_lastmonth`.

## 6. `config_refresh`
**Purpose**: Regenerates dynamic URLs or system configurations.
- When a user updates system variables in `analysis_config`, these triggers rebuild external URLs (like TMS order execution links).
- **Attachments**: `analysis_config`, `raw_deb_nepseapi_marketdepth`.

---

## 7. Development Guidelines: `safeupdate` Extension
Supabase uses the PostgreSQL `safeupdate` extension for all API roles (`authenticated`, `anon`, `service_role`). This extension **strictly prohibits any `UPDATE` or `DELETE` statement that lacks a `WHERE` clause** to prevent accidental full-table modifications.

If a database trigger executes an `UPDATE` on a table without a `WHERE` clause (e.g. `UPDATE my_table SET updated_at = NOW();`), and that trigger is fired by an Edge Function or the REST API, **the entire API request will fail with a 500 Error: `UPDATE requires a WHERE clause`**.

**Rule**: Whenever writing a trigger that modifies a table, you MUST include a dummy `WHERE` clause (e.g., `WHERE primary_key IS NOT NULL`) if you intend to update all rows, to safely bypass the `safeupdate` restriction.
