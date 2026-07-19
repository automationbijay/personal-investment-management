# View: `view_mf_assets_value_change`

## Overview
`view_mf_assets_value_change` acts as the foundational calculation layer for estimating mutual fund NAV. It maps the individual stock holdings of every mutual fund (published monthly) and computes the exact monetary difference in value between the date the last NAV was published (weekly) and today's live market prices.

## Dependencies
*   `public.raw_mf_nepsealpha_assets_lastmonth`: Provides the quantity of each stock held by a mutual fund (monthly granularity).
*   `public.raw_mf_sharesansar_nav`: Provides the exact date the last weekly NAV was officially calculated.
*   `public.raw_price_history`: Provides the historical end-of-day price of the stock on the specific NAV publication date.
*   `public.raw_nepseapi_live_prices`: Provides the Latest Traded Price (LTP) of the stock today.

## Core Logic & Mathematics

1. **Date Binding**
   The view joins the `raw_price_history` table using the specific date provided in `raw_mf_sharesansar_nav`. This is critical: to know how much a portfolio has grown or shrunk, the calculation must start exactly from the day the last official NAV was pegged.
   *   `nav_date_price` = Price of the stock on the NAV date.

2. **Asset Valuation Computation**
   For every stock (`asset_symbol`) inside a mutual fund (`mf_symbol`):
   *   **`weekly_nav_value`**: `quantity * nav_date_price`
   *   **`today_nav_value`**: `quantity * today_ltp`
   *   **`nav_changed`**: `today_nav_value - weekly_nav_value`

3. **Missing Data Handling**
   If a stock is suspended, delisted, or newly listed, historical or live prices might be missing. The view flags these assets or assumes 0 change to prevent the entire fund calculation from failing.
