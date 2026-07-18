# View: `deb_ytm_analysis`

## Overview
`deb_ytm_analysis` is responsible for calculating the Yield to Maturity (YTM) for all listed debentures. Rather than just calculating a single YTM based on the Latest Traded Price (LTP), this view evaluates multiple market depth scenarios to show the user exactly what yield they will lock in if they execute immediately against the order book, or if they place a bid slightly ahead of the market.

## Dependencies
*   `public.raw_deb_nepsealpha_details`: Provides foundational debenture parameters such as `interest_rate`, `face_value` (1000), and `remaining_period_years`.
*   `public.raw_deb_nepseapi_marketdepth`: Provides the real-time order book (highest bids and lowest asks).
*   `public.raw_nepseapi_live_prices`: Supplies the Latest Traded Price (LTP) of the debenture.

## Core Logic & Mathematics

### The Yield to Maturity Approximation Formula
The core of this view is a PostgreSQL function (or mathematical equivalent) that uses the standard approximation formula for YTM:
$$ YTM \approx \frac{C + \frac{F - P}{n}}{\frac{F + P}{2}} $$
*   $C$: Annual Coupon Payment (`interest_rate * face_value / 100`)
*   $F$: Face Value (`1000`)
*   $n$: Years to Maturity (`remaining_period_years`)
*   $P$: The variable Price (LTP, Ask, or Bid)

### Scenarios Evaluated
The view computes YTM under several theoretical and practical pricing scenarios:
1.  **`ltp_ytm`**: Calculates YTM using the $P = \text{LTP}$. This represents the historical reality of the last trade.
2.  **`buy_at_ask_ytm`**: Calculates YTM using $P = \text{lowest\_ask\_price}$. This is the yield an investor locks in if they instantly buy the debenture from the cheapest willing seller right now.
3.  **`sell_at_bid_ytm`**: Calculates YTM using $P = \text{highest\_bid\_price}$. This is the yield a current holder accepts if they instantly dump their debentures onto the highest willing buyer.
4.  **`highest_bid_ytm`**: Calculates YTM using $P = \text{highest\_bid\_price} + 0.1$. This is a "Ticker Ahead" strategy (assuming a 0.1 tick size for debentures) where the user places a bid just above the current market to guarantee execution while maximizing yield.
5.  **`lowest_ask_ytm`**: Calculates YTM using $P = \text{lowest\_ask\_price} - 0.1$. A Ticker Ahead strategy for selling.

## Use Case
This view allows the system to identify highly lucrative, mispriced debentures sitting in the ask queue. If `buy_at_ask_ytm` > 12%, an investor can immediately execute the trade knowing the yield is guaranteed.
