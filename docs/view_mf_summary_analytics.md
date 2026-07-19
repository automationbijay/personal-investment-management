# Mutual Fund Summary Analytics (`view_mf_summary_analytics`)

The `view_mf_summary_analytics` is a comprehensive PostgreSQL View designed to aggregate granular stock-level portfolio changes and estimate the real-time Net Asset Value (NAV) of mutual funds between their official publication dates. 

It relies on a foundational view (`view_mf_assets_value_change`) to handle individual asset pricing, and then aggregates that data to the fund level.

---

## Column Breakdown & Calculation Logic

### 1. Identifiers & Base Metrics
* **`MF`**: The Mutual Fund's unique ticker symbol (e.g., `NICSF`, `C30MF`).
* **`total quantity`**: The total sum of all shares/units held by the mutual fund across its entire equity portfolio.
* **`skipped scripts due to no price data`**: A count of individual scrips (stock symbols) in the fund's portfolio that are completely excluded from the financial calculations due to missing Live Traded Prices (`LTP`) or missing historical weekly prices.
* **`quantity without price`**: The total volume of shares that belong to the "skipped scripts".

### 2. Portfolio Value Calculations
* **`last week value`**: The total estimated value of the fund's equity portfolio on the exact date the last Weekly NAV was published.
  * *Formula*: `SUM(quantity * historical_price_on_weekly_nav_date)`
* **`this week value`**: The total real-time value of the fund's equity portfolio based on today's Live Traded Prices (LTP).
  * *Formula*: `SUM(quantity * todays_ltp)`
* **`change in value`**: The absolute monetary gain or loss of the portfolio since the weekly NAV was published.
  * *Formula*: `this week value - last week value`
* **`value change percentate`**: The percentage growth or decline of the underlying equity portfolio.
  * *Formula*: `(change in value / last week value) * 100`

### 3. Third-Party Published Data
* **`SS weekly Date`**: The specific date the mutual fund last published its Weekly NAV on ShareSansar (Format: `MM/DD/YYYY`).
* **`SS weekly NAV`**: The official Weekly NAV value published on ShareSansar.
* **`Monthly Nav Month`**: The Nepali month string (e.g., "Jestha 2083") representing the most recent monthly portfolio disclosure on NEPSEAlpha.
* **`Capital_Market`**: The percentage of the mutual fund's total size allocated to the stock market / equities. (Sourced from NEPSEAlpha).
* **`Non_Capital_Market`**: The percentage of the mutual fund's total size allocated to fixed income, debentures, and cash.

### 4. Real-Time NAV Estimations
Because mutual funds only publish NAVs weekly, we estimate their daily real-time NAV using the underlying stock portfolio's performance.

* **`adjusted_nav`**: A simplified NAV estimation assuming 100% of the mutual fund's capital is invested in equities and moved synchronously with the stock portfolio.
  * *Formula*: `SS weekly NAV * (1 + (value change percentate / 100))`
* **`cap_market_adjusted_nav`**: A precise NAV estimation that adjusts the growth based strictly on the ratio of capital actually invested in the stock market. It assumes the `Non_Capital_Market` portion (cash/bonds) had 0% growth.
  * *Formula*: `SS weekly NAV * (1 + ((value change percentate / 100) * (Capital_Market / 100)))`

### 5. Market Premium & Discount Analysis
* **`mf_ltp`**: The current Live Traded Price (LTP) of the mutual fund unit itself on the secondary market.
* **`discount_premium_adjusted`**: The percentage difference between the mutual fund's market price (`mf_ltp`) and our simplified 100%-equity NAV estimation (`adjusted_nav`).
  * *Formula*: `((mf_ltp - adjusted_nav) / adjusted_nav) * 100`
* **`discount_premium_cap_market`**: The percentage difference between the mutual fund's market price (`mf_ltp`) and our precise capital-market NAV estimation (`cap_market_adjusted_nav`). 
  * *Formula*: `((mf_ltp - cap_market_adjusted_nav) / cap_market_adjusted_nav) * 100`

> **Note on Discount/Premium**: A **negative** value in these columns indicates the mutual fund is trading at a **discount** compared to the estimated real-time value of its underlying assets. A **positive** value indicates it is trading at a premium.

### 6. Static / Utility Columns
* **`NAV date Match Formula Date`**: Hardcoded to `TRUE` for internal system compatibility.
