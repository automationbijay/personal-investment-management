import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(os.environ.get("DATABASE_URL"))
cur = conn.cursor()

view_sql = """
CREATE OR REPLACE VIEW public.mf_ask_bid 
WITH (security_invoker = true)
AS
 WITH config AS (
         SELECT COALESCE(max(
                CASE
                    WHEN analysis_config.config_key = 'tick_size_mf'::text THEN analysis_config.config_value::numeric
                    ELSE NULL::numeric
                END), max(
                CASE
                    WHEN analysis_config.config_key = 'tick_size_default'::text THEN analysis_config.config_value::numeric
                    ELSE NULL::numeric
                END), 0.01) AS tick_size,
            COALESCE(max(
                CASE
                    WHEN analysis_config.config_key = 'default_bid_discount_percent'::text THEN analysis_config.config_value::numeric
                    ELSE NULL::numeric
                END), 5::numeric) AS def_bid_disc,
            COALESCE(max(
                CASE
                    WHEN analysis_config.config_key = 'default_ask_premium_percent'::text THEN analysis_config.config_value::numeric
                    ELSE NULL::numeric
                END), 5::numeric) AS def_ask_prem,
            COALESCE(max(
                CASE
                    WHEN analysis_config.config_key = 'minimum_transaction_value'::text THEN analysis_config.config_value::numeric
                    ELSE NULL::numeric
                END), 0::numeric) AS min_tx_val
           FROM analysis_config
        ), md_parsed AS (
         SELECT md.symbol,
            b_max.highest_bid,
            b_max.highest_bid_qty,
            a_min.lowest_ask,
            a_min.lowest_ask_qty
           FROM raw_marketdepth_nepseapi_new md
             CROSS JOIN config c
             LEFT JOIN LATERAL ( SELECT (b.value ->> 'orderBookOrderPrice'::text)::numeric AS highest_bid,
                    (b.value ->> 'quantity'::text)::numeric AS highest_bid_qty
                   FROM jsonb_array_elements(md.buy_market_depth) b(value)
                  WHERE ((b.value ->> 'orderBookOrderPrice'::text)::numeric) > 0::numeric AND (((b.value ->> 'quantity'::text)::numeric) * ((b.value ->> 'orderBookOrderPrice'::text)::numeric)) >= c.min_tx_val
                  ORDER BY ((b.value ->> 'orderBookOrderPrice'::text)::numeric) DESC
                 LIMIT 1) b_max ON true
             LEFT JOIN LATERAL ( SELECT (a.value ->> 'orderBookOrderPrice'::text)::numeric AS lowest_ask,
                    (a.value ->> 'quantity'::text)::numeric AS lowest_ask_qty
                   FROM jsonb_array_elements(md.sell_market_depth) a(value)
                  WHERE ((a.value ->> 'orderBookOrderPrice'::text)::numeric) > 0::numeric AND (((a.value ->> 'quantity'::text)::numeric) * ((a.value ->> 'orderBookOrderPrice'::text)::numeric)) >= c.min_tx_val
                  ORDER BY ((a.value ->> 'orderBookOrderPrice'::text)::numeric)
                 LIMIT 1) a_min ON true
        ), calculations AS (
         SELECT nav."MF" AS symbol,
            nav.adjusted_nav,
            nav.mf_ltp,
            p.highest_bid,
            p.highest_bid_qty,
            p.lowest_ask,
            p.lowest_ask_qty,
            c.tick_size,
            c.def_bid_disc,
            c.def_ask_prem,
                CASE
                    WHEN p.highest_bid IS NOT NULL THEN p.highest_bid + c.tick_size
                    ELSE nav.adjusted_nav * (1::numeric - c.def_bid_disc / 100::numeric)
                END AS my_bid,
                CASE
                    WHEN p.lowest_ask IS NOT NULL THEN p.lowest_ask - c.tick_size
                    ELSE nav.adjusted_nav * (1::numeric + c.def_ask_prem / 100::numeric)
                END AS my_ask,
            nav.mf_ltp * (1::numeric - c.def_bid_disc / 100::numeric) AS lower_limit,
            nav.mf_ltp * (1::numeric + c.def_ask_prem / 100::numeric) AS upper_limit,
            w."WACC Rate"::numeric AS wacc_rate
           FROM vw_mf_summary_analytics nav
             JOIN md_parsed p ON nav."MF" = p.symbol::text
             CROSS JOIN config c
             LEFT JOIN raw_meroshare_wacc w ON nav."MF" = w.symbol
        )
 SELECT symbol,
    adjusted_nav,
    mf_ltp AS ltp,
    round((mf_ltp - adjusted_nav) / adjusted_nav * 100::numeric, 4) AS discount_at_ltp,
    highest_bid,
    highest_bid_qty,
    lowest_ask,
    lowest_ask_qty,
    my_bid,
    my_ask,
    round((my_bid - adjusted_nav) / adjusted_nav * 100::numeric, 4) AS my_bid_discount_premium,
    round((my_ask - adjusted_nav) / adjusted_nav * 100::numeric, 4) AS my_ask_discount_premium,
    round(lower_limit, 2) AS lower_limit_price,
    round(upper_limit, 2) AS upper_limit_price,
    round((lower_limit - adjusted_nav) / adjusted_nav * 100::numeric, 4) AS lower_limit_discount_premium,
    round((upper_limit - adjusted_nav) / adjusted_nav * 100::numeric, 4) AS upper_limit_discount_premium,
    wacc_rate,
    round((mf_ltp - wacc_rate) / NULLIF(wacc_rate, 0) * 100::numeric, 4) AS profit_loss_pct_at_ltp,
    round((my_ask - wacc_rate) / NULLIF(wacc_rate, 0) * 100::numeric, 4) AS profit_loss_pct_at_my_ask,
    round((my_bid - wacc_rate) / NULLIF(wacc_rate, 0) * 100::numeric, 4) AS profit_loss_pct_at_my_bid
   FROM calculations;
"""
cur.execute(view_sql)
conn.commit()

print("View mf_ask_bid updated successfully!")

cur.close()
conn.close()
