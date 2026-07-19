# Database Views Documentation

This directory contains the detailed mathematical and architectural documentation for the analytical PostgreSQL views used in the Investment Management Database.

## Mutual Fund Views
*   [view_mf_assets_value_change](view_mf_assets_value_change.md): Tracks real-time asset changes for mutual fund stock portfolios.
*   [view_mf_summary_analytics](view_mf_summary_analytics.md): The core valuation engine calculating daily Estimated NAV.
*   [view_mf_ask_bid](view_mf_ask_bid.md): Simulates live order-book execution opportunities, ticker-ahead pricing, and dynamic circuit limits.

## Debenture Views
*   [view_deb_ytm_analysis](view_deb_ytm_analysis.md): Calculates live Yield to Maturity parameters (Buy/Sell scenarios).
*   [deb_market_analytics](deb_market_analytics.md): Aggregates base debenture analytics.

## Portfolio & Personal Wealth
*   [wiki_profit_loss_analysis](../wiki_profit_loss_analysis.md): Tracks real-time profit and loss (PnL) for the user's investment portfolio based on WACC and live market pricing.
