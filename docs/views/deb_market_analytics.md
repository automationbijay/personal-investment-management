# View: `deb_market_analytics`

## Overview
`deb_market_analytics` aggregates foundational debenture analytics and live market pricing data. While `deb_ytm_analysis` focuses heavily on the yield calculations via the order book, this view provides a broader snapshot of the debenture's standing.

## Dependencies
*   `public.raw_deb_nepsealpha_details`: Provides foundational debenture parameters such as `interest_rate`, `face_value` (1000), `maturity_date`, and `remaining_period_years`.
*   `public.raw_nepseapi_live_prices`: Supplies the Latest Traded Price (LTP) and daily change metrics for the debenture.

## Core Logic & Mathematics
This view primarily serves as a clean join mechanism, ensuring that whenever a frontend or analytical script queries debenture health, they do not need to manually parse the static characteristics against live data. It joins the static maturity details (from the monthly/annual scraper) with the high-frequency daily price updates (from the live API).
