# NEPSE Constraints & Data Limitations

This document tracks known limitations, data gaps, and structural constraints of the Nepal Stock Exchange (NEPSE) and related financial data sources (like NEPSE API, ShareSansar, NEPSEAlpha) that directly impact our database architecture.

## 1. Unlisted Open-Ended Mutual Funds
**The Constraint**: 
NEPSE only lists **closed-end** mutual funds on its official exchange. **Open-ended** mutual funds (such as `ELIS` - Everest Large Investment Scheme, or `NICAELIS`) are NOT traded on the secondary market and therefore do NOT exist in the official NEPSE API `CompanyList` or `SecurityList`.

**The Impact**: 
When scraping monthly asset portfolios of other mutual funds, you will occasionally find that they hold these open-ended mutual funds as assets. Because our database enforces strict referential integrity (Foreign Keys) to the `raw_securities` table, inserting a portfolio containing an open-ended mutual fund (like `ELIS`) will cause a foreign key violation and crash the import, because the symbol is missing from `raw_securities`.

**The Solution**:
When new open-ended mutual funds are introduced to the market, they must be **manually inserted** into the `raw_securities` table as placeholders (with `active_status = 'A'`) before the portfolio scrapers can successfully insert them into `raw_mf_nepsealpha_assets_lastmonth`. 

*Example manual insertion:*
```sql
INSERT INTO public.raw_securities (id, symbol, security_name, name, active_status)
VALUES (
    (SELECT COALESCE(MAX(id), 0) + 1 FROM public.raw_securities),
    'ELIS',
    'Everest Large Investment Scheme',
    'Everest Large Investment Scheme',
    'A'
) ON CONFLICT (symbol) DO NOTHING;
```
