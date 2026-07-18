# Database Audit Report

## Row Level Security (RLS)
All tables have RLS enabled.

## Missing Foreign Key Indexes
All foreign keys are indexed.

## Views Security
> [!WARNING]
> The following views do not have `security_invoker = true`. They will bypass RLS.
- mf_assets_value_change
- vw_mf_summary_analytics

## Security Definer Functions
No SECURITY DEFINER functions found in public schema.

## Custom Indexes (Check for redundancy)
Review these indexes. If they duplicate primary key indexes, they should be removed per `AGENTS.md` rules.
- Table `raw_mf_nepsealpha_assets_lastmonth`, Index `idx_raw_mf_nepsealpha_assets_lastmonth_symbol`: `CREATE INDEX idx_raw_mf_nepsealpha_assets_lastmonth_symbol ON public.raw_mf_nepsealpha_assets_lastmonth USING btree (symbol)`
- Table `raw_mf_nepsealpha_assets_lastmonth`, Index `idx_raw_mf_nepsealpha_assets_lastmonth_month`: `CREATE INDEX idx_raw_mf_nepsealpha_assets_lastmonth_month ON public.raw_mf_nepsealpha_assets_lastmonth USING btree ("Month")`
- Table `raw_price_history`, Index `idx_raw_price_history_date`: `CREATE INDEX idx_raw_price_history_date ON public.raw_price_history USING btree ("Date")`
- Table `mf_assets_analytics`, Index `idx_mf_assets_analytics_symbol`: `CREATE INDEX idx_mf_assets_analytics_symbol ON public.mf_assets_analytics USING btree (symbol)`
- Table `mf_assets_analytics`, Index `idx_mf_assets_analytics_month`: `CREATE INDEX idx_mf_assets_analytics_month ON public.mf_assets_analytics USING btree ("Month")`
- Table `fundamental_data`, Index `idx_fundamental_data_date`: `CREATE INDEX idx_fundamental_data_date ON public.fundamental_data USING btree (date)`
- Table `deb_price_stats`, Index `idx_deb_price_stats_symbol`: `CREATE UNIQUE INDEX idx_deb_price_stats_symbol ON public.deb_price_stats USING btree ("Symbol")`
