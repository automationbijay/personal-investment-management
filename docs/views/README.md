# Database Views Documentation

This directory contains the detailed mathematical and architectural documentation for the analytical PostgreSQL views used in the Investment Management Database.

## Mutual Fund Views
*   [mf_assets_value_change](mf_assets_value_change.md): Tracks real-time asset changes for mutual fund stock portfolios.
*   [vw_mf_summary_analytics](vw_mf_summary_analytics.md): The core valuation engine calculating daily Estimated NAV.
*   [mf_ask_bid](mf_ask_bid.md): Simulates live order-book execution opportunities, ticker-ahead pricing, and dynamic circuit limits.

## Debenture Views
*   [deb_ytm_analysis](deb_ytm_analysis.md): Calculates live Yield to Maturity parameters (Buy/Sell scenarios).
*   [deb_market_analytics](deb_market_analytics.md): Aggregates base debenture analytics.

## Portfolio & Personal Wealth
*   [vw_profit_loss_analysis](vw_profit_loss_analysis.md): Evaluates real-time PnL against weighted average cost of capital (WACC) for personal holdings.
