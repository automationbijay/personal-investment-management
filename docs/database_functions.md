# Database Functions

The following custom PL/pgSQL functions exist in the PostgreSQL `public` schema to power database triggers and complex mathematical calculations.

## 1. `fn_sync_wiki_profit_loss()`
*   **Type**: Trigger Function
*   **Purpose**: Optimizes real-time PnL tracking. When a live price, holding quantity, or WACC changes for a specific `symbol`, this function executes an `UPSERT` on the `wiki_profit_loss_analysis` table for that exact symbol alone, avoiding full-table recalculations.
*   **Attached to**: `raw_meroshare_portfolio`, `raw_nepseapi_live_prices`, `raw_meroshare_wacc`.

## 2. `calculate_ytm()`
*   **Type**: Standard Function
*   **Purpose**: Evaluates Yield to Maturity (YTM) for debentures using the standard financial approximation formula.
*   **Usage**: Invoked dynamically by views like `view_deb_ytm_analysis` to map live market depth (ask/bid prices) to various yield scenarios.

## 3. `fn_auto_create_missing_fks()` / `trg_insert_missing_security()`
*   **Type**: Trigger Function
*   **Purpose**: Foreign key resilience. Automatically intercepts insertions referencing unrecognized stock symbols, creates a stub record in the master `raw_securities` table, and then allows the original insertion to proceed without constraint errors.

## 4. `update_updated_at_column()` / `moddatetime()`
*   **Type**: Trigger Function
*   **Purpose**: Standard utility function that sets a table's `updated_at` column to `CURRENT_TIMESTAMP`.
*   **Usage**: Used by all `timestamp_auto` category triggers.

## 5. `trg_update_script_health()`
*   **Type**: Trigger Function
*   **Purpose**: Powers the `health_auto` triggers by taking the current table name (from `TG_TABLE_NAME`) and `UPSERT`ing a success log entry into the `sys_script_health` table.

## 6. `fn_update_mf_analytics_on_price_change()` / `refresh_on_portfolio_update()`
*   **Type**: Trigger Function
*   **Purpose**: Powers the `analytics_sync` triggers to flag or update downstream analytical materializations when raw historical prices or portfolio structures change.

## 7. `generate_tms_order_urls()` / `refresh_urls_on_config_update()`
*   **Type**: Trigger Function
*   **Purpose**: Generates dynamic URLs based on configuration parameters defined in the database (used by `config_refresh` triggers).

## 8. `fn_cron_populate_averages()`
*   **Type**: Cron Function
*   **Purpose**: Scheduled by `pg_cron` to compute the 5, 10, and 30-day moving averages (LTP, Volume, VWAP) daily at 4:00 PM and store them in `wiki_average`.

## 9. `fn_cron_populate_profit_loss()`
*   **Type**: Cron Function
*   **Purpose**: Scheduled by `pg_cron` to perform a full-table PnL recalculation every 5 hours for the `wiki_profit_loss_analysis` table as a self-healing sync.
