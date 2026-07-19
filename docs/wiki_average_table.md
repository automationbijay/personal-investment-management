# Stock Averages Tracking (`wiki_average` table)

## Overview
The `wiki_average` table acts as a daily snapshot that stores pre-calculated moving averages (5-day, 10-day, 30-day, and all-time) for key stock metrics including **LTP** (Last Traded Price), **Volume**, and **VWAP** (Volume Weighted Average Price).

Since calculating rolling averages across the entire `raw_price_history` dataset on the fly (via a dynamic VIEW) can become computationally expensive as the dataset grows, this information is stored as a physical snapshot table that gets refreshed daily.

## Table Schema (`public.wiki_average`)

| Column Name      | Type           | Description                                                                 |
| :---             | :---           | :---                                                                        |
| `symbol`         | `VARCHAR(PK)`  | Primary Key. Foreign key referencing `raw_securities(symbol)`.              |
| `Date`           | `DATE`         | The date on which the moving average was last calculated (typically today). |
| `ltp_avg_5d`     | `NUMERIC(15,2)`| 5-day moving average of Last Traded Price (rounded to 2 decimal places).    |
| `ltp_avg_10d`    | `NUMERIC(15,2)`| 10-day moving average of Last Traded Price.                                 |
| `ltp_avg_30d`    | `NUMERIC(15,2)`| 30-day moving average of Last Traded Price.                                 |
| `ltp_avg_all`    | `NUMERIC(15,2)`| All-time average of Last Traded Price.                                      |
| `volume_avg_*`   | `NUMERIC(15,2)`| 5, 10, 30, and all-time moving averages for Trade Volume.                   |
| `vwap_avg_*`     | `NUMERIC(15,2)`| 5, 10, 30, and all-time moving averages for VWAP.                           |
| `created_at`     | `TIMESTAMPTZ`  | Timestamp when the record was first inserted.                               |
| `updated_at`     | `TIMESTAMPTZ`  | Timestamp when the snapshot was last refreshed.                             |

> [!NOTE]
> All averages are aggressively cast and rounded to `NUMERIC(15, 2)` inside the database query to guarantee consistency and max 2 decimal places.

## Data Source & Automation

The table is populated by a Python script:
[`scripts/sync_data/populate_averages.py`](file:///c:/Users/purib/Desktop/investmetn%20management%20supabse%20db/scripts/sync_data/populate_averages.py)

### Execution
This script is designed to run **once daily** (ideally after market close) to refresh the snapshot for all symbols.

```bash
# Run manually
python scripts/sync_data/populate_averages.py
```

### Calculation Logic
The Python script connects to PostgreSQL and uses a single heavily optimized UPSERT (`INSERT ... ON CONFLICT DO UPDATE`) query. It relies on PostgreSQL Window Functions:

1. **Partition & Rank**: It assigns a `ROW_NUMBER()` to every row in `raw_price_history`, grouped by `symbol` and ordered by `Date DESC`. This ranks the most recent price history as `1`, the day prior as `2`, and so on.
2. **Filter & Average**: It utilizes SQL aggregation filters (`FILTER (WHERE rn <= 5)`) to cleanly average only the past *N* trading days without needing subqueries or self-joins.
3. **Upsert**: It overrides the existing row in `average` for each symbol, making it a "snapshot" of the current day's averages.
