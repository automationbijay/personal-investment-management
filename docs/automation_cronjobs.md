# Automation & Cronjobs

The investment database relies on several background Python scripts located in the `scripts/sync_data/` directory to scrape external sources, update historical models, and persist daily views. 

To keep the database fresh, these scripts should be executed automatically on a schedule (e.g., using GitHub Actions, Windmill, cron, or n8n).

## 1. Database-Native `pg_cron` Jobs
The database natively schedules and executes internal sync logic using the `pg_cron` extension. These do NOT require external runners.

*   **Averages Job** (`fn_cron_populate_averages`)
    *   **Purpose**: Computes 5, 10, and 30-day moving averages and stores them in `wiki_average`.
    *   **Schedule**: Runs daily at 4:00 PM (`0 16 * * *`).
*   **PnL Full Sync** (`fn_cron_populate_profit_loss`)
    *   **Purpose**: Runs a full-table PnL recalculation as a self-healing sync.
    *   **Schedule**: Runs every 5 hours (`0 */5 * * *`).

## 2. Supabase Edge Functions (TypeScript/Deno)
These scripts fetch external data from the internet. They have been ported to Supabase Edge Functions, which can be triggered on a schedule natively using Supabase Cron.

*   **`check-market-status`** (`supabase/functions/check-market-status`)
    *   **Purpose**: Checks `/IsNepseOpen` and upserts the result to `analysis_config` (`is_market_open`). The other Edge Functions read this value and abort if the market is closed to save compute.
    *   **Schedule**: Daily at 11:00 AM.
*   **`sync-sharesansar`** (`supabase/functions/sync-sharesansar`)
    *   **Purpose**: Scrapes the weekly NAV of mutual funds from ShareSansar into `raw_mf_sharesansar_nav`.
    *   **Schedule**: Weekly (Friday evenings or Sunday mornings).
*   **`sync-securities`** (`supabase/functions/sync-securities`)
    *   **Purpose**: Updates the master list of all tradable symbols (`raw_securities`) from the NEPSE API.
    *   **Schedule**: Weekly.

## Deployment & Execution
To deploy the Edge Functions, you must use the Supabase CLI:

```bash
# Deploy to your Supabase project
supabase functions deploy check-market-status
supabase functions deploy sync-securities
supabase functions deploy sync-sharesansar
```
