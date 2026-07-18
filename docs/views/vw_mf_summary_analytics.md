# View: `vw_mf_summary_analytics`

## Overview
`vw_mf_summary_analytics` is the core valuation engine for Mutual Funds within the system. Since mutual funds in Nepal only publish their actual Net Asset Value (NAV) weekly, this view dynamically estimates the NAV daily based on the fluctuating values of the underlying assets held in their portfolio.

## Dependencies
*   `public.mf_assets_value_change`: Provides the granular calculation of how much the value of each individual stock in a mutual fund's portfolio has changed since the last official weekly NAV publication date.
*   `public.raw_mutual_funds`: The master table of mutual funds.
*   `public.raw_mf_sharesansar_nav`: The raw, official weekly NAV data scraped from ShareSansar.
*   `public.raw_nepseapi_live_prices`: Supplies the Latest Traded Price (LTP) of the mutual fund itself.

## Core Logic & Mathematics

1. **Portfolio Aggregation**
   The view aggregates the individual asset changes calculated in `mf_assets_value_change`.
   *   `total_weekly_value = SUM(weekly_nav_value)`
   *   `total_current_value = SUM(today_nav_value)`
   *   `total_change = total_current_value - total_weekly_value`

2. **Capital Market Adjustment**
   Mutual funds do not invest 100% of their capital into the stock market. A portion is held in fixed deposits, debentures, or cash. To prevent overestimating the volatility of the NAV, the view adjusts the stock market gains/losses based on the fund's known equity allocation (Capital Market %).
   *   `weighted_avg_change_pct = (total_change / total_weekly_value) * 100`
   *   `capital_market_adj_change_pct = weighted_avg_change_pct * (Capital_Market / 100)`

3. **Daily Estimated NAV (`adjusted_nav`)**
   The final estimated NAV applies the adjusted change percentage to the last official weekly NAV.
   *   `adjusted_nav = SS_weekly_Nav * (1 + capital_market_adj_change_pct / 100)`

4. **Premium/Discount Analysis**
   Evaluates how the mutual fund is trading on the live market relative to its intrinsic estimated value.
   *   `discount_premium_adjusted = ((mf_ltp - adjusted_nav) / adjusted_nav) * 100`
   *   *(Note: A negative value signifies the fund is trading at a discount).*
