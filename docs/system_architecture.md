# Investment Management System

## Overview
The Investment Management System is a specialized screening and recommendation engine focused primarily on Mutual Funds (MFs) and Debentures in the Nepalese stock market. It aggregates live market data and NAV reports to calculate real-time discounts and Yield to Maturity (YTM) for instant buy/sell recommendations.

## Data Sources & Ingestion

### 1. Mutual Funds Data
*   **Weekly & Monthly NAV Numbers:** Scraped from [ShareSansar](https://www.sharesansar.com/mutual-fund-navs).
*   **Monthly Portfolio Holdings & Asset Allocations:** Scraped from [NEPSEAlpha](https://nepsealpha.com/mutual-fund-navs).

### 2. Debenture Data
*   **Debenture Tracking:** Scraped from [NEPSEAlpha](https://nepsealpha.com/debenture) (likely via GitHub Actions).

### 3. Live Market Data (NEPSE)
*   **Source:** Custom API at [neps.puribijay.com.np](https://neps.puribijay.com.np/) (Docs at `/docs`) and the `/SecurityList` endpoint.
*   **Data Points:** Real-time market depth, live prices (Bid/Ask), master list of tradable securities.
*   **Tables:** `raw_deb_nepseapi_marketdepth`, `raw_securities`, `raw_nepseapi_live_prices`

### 4. Portfolio Data (Meroshare)
*   **Data Points:** Current Holdings, Transaction History, WACC (Cost of Capital).
*   **Purpose:** To cross-reference current portfolio with the buy/sell signals.

## Core Investment Logic

### Mutual Funds (MFs) Screening
*   **Logic:** Estimate the **Daily NAV** by adjusting the latest official NAV with real-time portfolio changes (tracked via individual stock LTPs). Then, calculate the discount (or premium) of the Current Market Price (CMP) against this **Estimated Daily NAV**.
*   **Recommendation:** Instant buy/sell signals based on the percentage of discount relative to the live estimated valuation.

### Debentures Screening
*   **Logic:** Calculate the Yield to Maturity (YTM) at the current live bid/ask price.
*   **Recommendation:** Instant buy/sell signals based on attractive YTM thresholds.

## Tech Stack
*   **Database:** Supabase (PostgreSQL)
*   **Scraping Tools:** Windmill, GitHub Actions, Playwright (Preferred for Python scripts)
*   **Live Data API:** Custom backend (neps.puribijay.com.np)

## Architecture & Data Flow
1. **Data Ingestion:** Scrapers (Windmill/GitHub Actions) periodically fetch NAV and Debenture data and push it to Supabase.
2. **Real-time Engine:** The system fetches live market depth/prices from the custom API.
3. **Calculation & Screening:** The engine calculates real-time **Estimated Daily NAVs** for MFs (adjusting for live stock holdings changes) and live **YTM** for Debentures.
4. **Actionable Output:** Highlights instant buy/sell opportunities.
