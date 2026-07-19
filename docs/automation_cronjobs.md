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
*   **`sync_gold_rates`** (`supabase/functions/sync_gold_rates`)
    *   **Purpose**: Scrapes gold and silver rates from multiple sources (Ashesh, HamroPatro) and stores the JSON data in `analysis_config` under the keys `gold_rates_ashesh` and `gold_rates_hamrobazar`.
    *   **Schedule**: Daily.
*   **`sync_sharesansar_daily_price`** (`supabase/functions/sync_sharesansar_daily_price`)
    *   **Purpose**: Scrapes the daily "Today Share Price" list from ShareSansar and upserts it into `raw_sharesansar_daily_price`.
    *   **Schedule**: Daily at 4:00 PM.
*   **`sync_sharesansar_promoter_lockin`** (`supabase/functions/sync_sharesansar_promoter_lockin`)
    *   **Purpose**: Scrapes the locked and unlocked promoter share details from ShareSansar and upserts into `raw_sharesansar_promoter_lockin`.
    *   **Schedule**: Every 5 days at 5:00 PM (Cron: `0 17 */5 * *`).

## Deployment & Execution
To deploy the Edge Functions, you must use the Supabase CLI:

```bash
# Deploy to your Supabase project
supabase functions deploy check-market-status
supabase functions deploy sync-securities
supabase functions deploy sync-sharesansar
supabase functions deploy sync_gold_rates
supabase functions deploy sync_sharesansar_daily_price
supabase functions deploy sync_sharesansar_promoter_lockin
```
