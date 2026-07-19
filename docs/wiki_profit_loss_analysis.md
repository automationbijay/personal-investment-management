# Table: `wiki_profit_loss_analysis`

## Overview
`wiki_profit_loss_analysis` is a PostgreSQL table designed to provide a real-time, consolidated view of an investor's unrealized profit or loss (PnL) for their entire stock portfolio. It is populated by a recurring Python sync script (`populate_profit_loss.py`).

## Dependencies
*   `public.raw_meroshare_portfolio`: Provides the quantity of shares held by the user for each security (`symbol`).
*   `public.raw_meroshare_wacc`: Provides the user's specific weighted average purchase price per share (`wacc`).
*   `public.raw_nepseapi_live_prices`: Supplies the Latest Traded Price (LTP).

## Core Logic & Mathematics

1. **Mapping and Cost Basis**
   The view maps `symbol` across the three tables.
   *   **Total Investment Value**: `quantity * wacc`
   *   This represents the actual out-of-pocket cost of acquiring the holdings, including commissions and fees.

2. **Current Valuation**
   *   **Total Current Value**: `quantity * ltp`
   *   This represents the gross value if the user were to liquidate the entire position at the current market rate.

3. **Profit & Loss Metrics**
   *   **Absolute Profit/Loss**: `(quantity * ltp) - (quantity * wacc)`
   *   **Profit/Loss Percentage**: `((ltp - wacc) / wacc) * 100`

## Use Case
This view serves as the primary data source for the user's personal dashboard. It triggers automated notifications or investment signals if certain stocks cross configured profit-taking or stop-loss thresholds.
