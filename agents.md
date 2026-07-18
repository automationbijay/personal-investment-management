# Developer & AI Agent Guidelines (agents.md)

This file defines the architecture, database naming conventions, core financial calculations, and data sources for the Investment Management Database. All agents and developers must strictly follow these specifications when modifying or extending this codebase.

For definitions of financial, database, and system terminology used in this repository, see the [Glossary of Terms](file:///c:/Users/purib/Desktop/investmetn%20management%20supabse%20db/docs/glossary.md).

---

## 1. Database Naming Conventions
The PostgreSQL database (Supabase) uses specific prefixes to distinguish between raw scraped data, aggregated analytics, and asset classes:

*   **`raw_` Prefix**: Holds raw, unfiltered data scraped from third-party services.
    *   *Example*: `raw_securities` (Master list of tradable securities, `symbol` is the Primary Key).
    *   *Example*: `raw_mutual_funds` (Master table of mutual funds, `symbol` is the Primary Key. Only stores symbol and timestamps; details are in child tables).
    *   *Example*: `raw_nepseapi_live_prices` (Stores a single row per symbol for the latest real-time LTP. 1:1 relation to `raw_securities`).
    *   *Example*: `raw_price_history` (Stores end-of-day historical prices. 1:N relation to `raw_securities`).
    *   *Example*: `raw_mf_sharesansar_nav` (raw weekly NAV scraped from ShareSansar. 1:1 relation to `raw_mutual_funds`).
    *   *Example*: `raw_deb_nepsealpha_details` (raw debenture parameters scraped from NEPSEAlpha).
    *   *Example*: `raw_mf_nepsealpha_dividends` (raw mutual fund expected dividends scraped from NEPSEAlpha).
*   **`mf_` Prefix**: Holds processed data, daily valuations, and portfolio holding analytics for **Mutual Funds**.
    *   *Example*: `mf_assets_value_change` (tracks change in value for individual stocks within mutual fund portfolios).
    *   *Example*: `mf_assets_analytics` (stores final daily NAV estimation and discounts).
*   **`deb_` Prefix**: Holds analytics and views for **Debentures** (bonds).
    *   *Example*: `deb_ytm_analysis` (calculates Yield to Maturity based on current live market depth).

---

## 2. Core Data Sources
We aggregate market information from four main sources:

1.  **ShareSansar (`sharesansar.com`)**
    *   *Purpose*: Fast scraping of weekly mutual fund NAV values and latest traded prices (LTP) of the mutual funds.
    *   *Table*: `raw_mf_sharesansar_nav`
2.  **NEPSEAlpha (`nepsealpha.com`)**
    *   *Purpose*: Monthly mutual fund asset portfolios/stock holdings (`raw_mf_nepsealpha_assets_lastmonth`), asset allocations (`raw_mf_nepsealpha_assets_allocation`), and debenture details (`raw_deb_nepsealpha_details`).
3.  **MeroShare (`meroshare.com`)**
    *   *Purpose*: User portfolio holdings (`raw_meroshare_portfolio`) and weighted average cost of capital (`raw_meroshare_wacc`) to calculate personal gains and investment signals.
4.  **NEPSE API (`neps.puribijay.com.np`)**
    *   *Purpose*: Self-hosted API fetching live transaction prices, real-time market depth (bids/asks) from Nepal Stock Exchange (`nepalstock.com`), and the master Security List.
    *   *Table*: `raw_deb_nepseapi_marketdepth`, `raw_securities`, `raw_nepseapi_live_prices`

---

## 3. Market Hours & Timezone Constraints
*   **Market Hours**: Monday to Friday, **11:00 AM to 3:00 PM** (Kathmandu Time / `Asia/Kathmandu`, UTC+5:45).
*   **Market Closures**: Saturday and Sunday.
*   **Rule**: Daily calculations (LTP updates, live market depth, YTM recalculations) should prioritize running during market hours when bid/ask lists and transaction prices change in real-time.

---

## 4. Mutual Fund Valuation & Daily NAV Estimation Logic

### The Core Methodology
Since mutual funds only publish their portfolio holdings **monthly** and their NAV **weekly**, we estimate the daily NAV between publications. We assume that **no stock has been added or removed from the portfolio since the last monthly publication date**. 

### Mathematical Calculations
Daily NAV updates are processed via database triggers and functions (`fn_refresh_mf_assets_analytics`):

1.  **Compute Individual Asset Changes** (`mf_assets_value_change`):
    *   `weekly Nav Value` = $Quantity \times \text{Stock LTP at Weekly NAV Date}$
    *   `today's Nav Value` = $Quantity \times \text{Stock Today's LTP}$
    *   `nav changed` = $\text{today's Nav Value} - \text{weekly Nav Value}$
    *   *Note on NAV Dates*: The column `weekly_nav_date_actual` strictly binds the valuation to the exact date the NAV was published. If a stock in the portfolio didn't trade on that specific date (e.g. a Friday), the `fn_calculate_mf_asset_ltps` trigger will look up the older traded price, auto-insert a carry-forward row into `raw_price_history` for the NAV date, and link to it.
2.  **Aggregate Portfolio Changes** (`mf_assets_analytics`):
    *   $\text{total\_weekly\_value} = \sum (\text{weekly Nav Value})$
    *   $\text{total\_current\_value} = \sum (\text{today's Nav Value})$
    *   $\text{total\_change} = \text{total\_current\_value} - \text{total\_weekly\_value}$
3.  **Adjust for Capital Market Allocation**:
    *   Since a portion of the fund's size is held in Cash or Fixed Income (assumed stable), we adjust the change based on the Capital Market allocation percentage:
        $$\text{weighted\_avg\_change\_pct} = \left(\frac{\text{total\_change}}{\text{total\_weekly\_value}}\right) \times 100$$
        $$\text{capital\_market\_adj\_change\_pct} = \text{weighted\_avg\_change\_pct} \times \left(\frac{\text{Capital\_Market}}{100}\right)$$
4.  **Calculate Estimated Daily NAV**:
        $$\text{Today\_NAV} = \text{sharesansar\_Weekly\_Nav} \times \left(1 + \frac{\text{capital\_market\_adj\_change\_pct}}{100}\right)$$
5.  **Calculate Premium/Discount %**:
        $$\text{Premium\_Discount\_Pct} = \left(\frac{\text{Today\_LTP} - \text{Today\_NAV}}{\text{Today\_NAV}}\right) \times 100$$
        *(A negative percentage indicates the fund trades at a discount to its estimated holdings valuation).*

---

## 5. Debenture Yield to Maturity (YTM) Calculations
Debenture evaluation relies on the Yield to Maturity approximation formula. Calculations are performed inside the `calculate_ytm` database function:

### Approximation Formula
$$\text{YTM} \approx \frac{C + \frac{F - P}{n}}{\frac{F + P}{2}}$$

Where:
*   $C$ = Annual coupon payment = $\text{Interest\_Rate} \times \frac{\text{Face\_Value}}{100}$
*   $F$ = Face value (standardized to **1000** NPR)
*   $P$ = Price of the debenture (evaluated at LTP, Ask price, Bid price, or custom Bid/Ask +/- 0.1 margins)
*   $n$ = Remaining years to maturity = $\text{Remaining\_Period\_Years}$

### Views and Outputs (`deb_ytm_analysis`)
The analysis view maps live market depth to multiple YTM scenarios:
*   `buy_at_ask_ytm`: YTM if bought immediately at the lowest ask price.
*   `sell_at_bid_ytm`: YTM if sold immediately at the highest bid price.
*   `highest_bid_ytm`: YTM at `highest_bid_price + 0.1` (placing a bid just above market depth).
*   `lowest_ask_ytm`: YTM at `lowest_ask_price - 0.1` (placing an ask just below market depth).

---

## 6. Guidelines for Scripting and Database Sync
*   **Environment**: Always use `.env` containing `DATABASE_URL` in the project root. Never hardcode database credentials.
*   **Language**: Python is the preferred scripting language.
*   **Scraping & Automation**: Use Playwright for browser automation scripts. Prefer scheduling tasks via Windmill or GitHub Actions rather than long-running local daemons.
*   **Database Synchronization**: Rely on Postgres triggers to auto-update analytics when prices change (`fn_update_mf_analytics_on_price_change`).
    *   **Health Tracking**: All `raw_` tables have a `trg_auto_health` statement-level trigger attached. This automatically UPSERTs the latest execution time and a `SUCCESS (Auto-Trigger)` status into `sys_script_health` upon any `INSERT` or `UPDATE`. This removes the need for manual logging from external scripts or n8n workflows.
    *   **Foreign Key Auto-resolution**: `raw_meroshare_portfolio` has a `trg_ensure_security_exists` trigger that auto-inserts any missing `symbol` into the parent `raw_securities` table (calculating the next `id`) to prevent foreign key constraint violations from unrecognized stocks.
*   **Folder Structure**: 
    *   Store all temporary scripts, one-off test scripts, and scratch files in the `temp/` folder.
    *   Store all deprecated files, old CSVs, and replaced logic in the `archive/` folder.
    *   Store scripts designed to scrape or sync data from other sources to the database in the `scripts/sync_data/` folder.
    *   Keep the project root clean with only active code, `.env`, and `.gitignore`.

---

## 7. Database Indexing & Performance Rules
*   **No Redundant Indexes**: PostgreSQL automatically creates a B-tree index for `PRIMARY KEY` and `UNIQUE` constraints. Agents MUST NOT create duplicate manual indexes (e.g., `CREATE INDEX idx_symbol ON table (symbol)`) if the column is already a Primary Key or Unique Key. Redundant indexes slow down `INSERT/UPDATE` operations.
*   **Index Left-Prefix**: Do not create single-column indexes if a composite index already covers that column as its first (left-most) key (e.g., if a PK is `(MF, symbol)`, an index on `(MF)` is redundant).
*   **Foreign Key Indexes**: Always create indexes for columns that act as Foreign Keys to avoid sequential scans during cascading operations or joins (e.g., `CREATE INDEX ON table (foreign_key_column)`).
