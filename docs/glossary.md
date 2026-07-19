# Glossary of Terms

This glossary defines domain-specific financial, database, and system terms used throughout this project.

---

## Financial & Market Terms

### 1. LTP (Latest Traded Price)
*   **Definition**: The most recent execution price of a transaction for a security on the Nepal Stock Exchange (NEPSE).
*   **Use Case**: Used to compute the real-time values of stock portfolios, current mutual fund valuations, and live debenture prices.

### 2. NAV (Net Asset Value)
*   **Definition**: The total asset value of a Mutual Fund minus its liabilities, divided by the total number of outstanding units.
*   **Frequency**: Published officially on a **weekly** basis (NAV number only) and **monthly** basis (full asset portfolio breakdown).
*   **Estimated NAV**: The system's calculated daily approximation of NAV between official publications, assuming portfolio components remain constant and adjusting for capital market allocation.

### 3. Debenture
*   **Definition**: A long-term debt instrument (bond) issued by companies/banks yielding a fixed coupon rate.
*   **Face Value (F)**: Standardized to **1000 NPR** per unit in the Nepalese market.

### 4. Yield to Maturity (YTM)
*   **Definition**: The total expected return of a debenture if held until it matures.
*   **Formula**: Approximated using:
    $$\text{YTM} \approx \frac{C + \frac{F - P}{n}}{\frac{F + P}{2}}$$
    where $C$ is coupon payment, $F$ is face value (1000), $P$ is purchase price, and $n$ is remaining years to maturity.

### 5. Bid & Ask
*   **Bid**: The highest price a buyer is willing to pay for a security (e.g., `highest_bid_price`).
*   **Ask**: The lowest price a seller is willing to accept for a security (e.g., `lowest_ask_price`).
*   **Spread**: The absolute price difference between the lowest ask and the highest bid (`lowest_ask_price - highest_bid_price`).
*   **Spread %**: The percentage difference relative to the ask:
    $$\text{Spread \%} = \left(\frac{\text{Spread}}{\text{lowest\_ask\_price}}\right) \times 100$$

### 6. WACC (Weighted Average Cost of Capital)
*   **Definition**: The average purchase price of shares/debentures in a user's portfolio, accounting for multiple buy transactions and charges.
*   **Use Case**: Sourced from MeroShare to evaluate personal net profit/loss and trigger personalized buy/sell actions.

### 7. Ticker Ahead Strategy
*   **Definition**: A simulated trading approach where an order is placed exactly one tick (`0.01` NPR or as configured via `tick_size_mf`) better than the current highest bid or lowest ask. 
*   **Use Case**: Used in `view_mf_ask_bid` and debenture YTM to estimate execution probabilities and compute best-case premium/discounts.

### 8. Minimum Transaction Value
*   **Definition**: A noise-filtering threshold defined in `analysis_config`. Orders in the market depth where `quantity * price` is below this value are ignored when determining the highest bid or lowest ask.

### 9. Circuit Limits & Fallbacks
*   **Definition**: The absolute upper and lower price boundaries dynamically configured via `default_ask_premium_percent` and `default_bid_discount_percent` in `analysis_config`. 
*   **Use Case**: Used to calculate `lower_limit_price` and `upper_limit_price` directly from the LTP. Also serves as fallback pricing when the real-time order book depth is entirely empty.

---

## Data & System Terms

### 1. Raw Data (`raw_` tables)
*   **Definition**: Raw data scraped from third-party websites before processing. 
*   **Scope**: Scraper jobs are independent background services (e.g., Windmill, GitHub Actions) and are *outside the scope* of this repository's calculation engine.

### 2. Nepalese Market Time constraints
*   **Market Hours**: Monday to Friday, **11:00 AM to 3:00 PM** (Kathmandu Time, UTC+5:45).
*   **Market Closure**: Saturday and Sunday.

### 3. TMS (Trade Management System)
*   **Definition**: The platform through which retail investors place orders on NEPSE. Order execution URLs are generated based on bid/ask analytics.

### 4. RTA (Registrar to the Share / Transfer Agent)
*   **Definition**: The commercial entity/bank handling register of debenture holders, distributions, and transfer procedures.
