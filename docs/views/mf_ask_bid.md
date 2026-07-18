# View: `mf_ask_bid`

## Overview
`mf_ask_bid` is a dynamic PostgreSQL view designed to identify real-time pricing opportunities for Mutual Funds based on live NEPSE order book data. It calculates the precise discount or premium available if a user were to execute a "Ticker Ahead" strategy (beating the best bidder or seller by exactly one tick) or if they trade at the absolute daily circuit limits.

## Dependencies
*   `public.vw_mf_summary_analytics`: Supplies the `adjusted_nav` and `mf_ltp` (Latest Traded Price).
*   `public.raw_marketdepth_nepseapi_new`: Supplies the live `buy_market_depth` and `sell_market_depth` JSONB arrays.
*   `public.analysis_config`: Supplies the noise filter threshold (`minimum_transaction_value`), the tick size (`tick_size_mf` or `tick_size_default`), and the dynamic circuit limit boundaries (`default_bid_discount_percent`, `default_ask_premium_percent`).

## Core Logic & Mathematics

1. **Order Book Filtering (Noise Reduction)**
   The view parses the JSON arrays of bids and asks. It ignores any orders where `(quantity * price) < minimum_transaction_value`. This prevents small "noise" orders from distorting the calculated highest bid or lowest ask.
   *   *Highest Valid Bid (`highest_bid`)*: The maximum price among valid buy orders.
   *   *Lowest Valid Ask (`lowest_ask`)*: The minimum price among valid sell orders.

2. **Ticker Ahead Simulation**
   *   **`my_bid`**: Calculates `highest_bid + tick_size`. This represents the price an investor should place to become the absolute top bidder. If the order book is empty, it falls back to the lower circuit limit (`adjusted_nav * (1 - default_bid_discount_percent / 100)`).
   *   **`my_ask`**: Calculates `lowest_ask - tick_size`. This represents the price an investor should place to become the cheapest seller. If empty, it falls back to the upper circuit limit (`adjusted_nav * (1 + default_ask_premium_percent / 100)`).
   
3. **Discount/Premium Computations**
   All metrics are benchmarked against the `adjusted_nav`. A negative percentage indicates a discount, while a positive indicates a premium.
   *   **`discount_at_ltp`**: `((mf_ltp - adjusted_nav) / adjusted_nav) * 100`
   *   **`my_bid_discount_premium`**: `((my_bid - adjusted_nav) / adjusted_nav) * 100`
   *   **`my_ask_discount_premium`**: `((my_ask - adjusted_nav) / adjusted_nav) * 100`

4. **Circuit Limits**
   Calculates the absolute maximum and minimum prices allowable by NEPSE for the day based on the LTP.
   *   **`lower_limit_price`**: `mf_ltp * (1 - default_bid_discount_percent / 100)`
   *   **`upper_limit_price`**: `mf_ltp * (1 + default_ask_premium_percent / 100)`
   *   **Limit Discounts/Premiums**: Evaluates how deep the discount would be if the stock hit its absolute lower circuit limit, or how high the premium if it hit the upper limit.
