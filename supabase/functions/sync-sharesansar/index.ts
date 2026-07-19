import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const cleanNumeric = (val: any) => {
  if (val === null || val === undefined || val === '') return null;
  if (typeof val === 'string') {
    val = val.replace(/,/g, '')
  }
  const parsed = parseFloat(val)
  return isNaN(parsed) ? null : parsed
}

const convertDate = (val: any) => {
  if (!val) return null;
  const parts = val.split('-')
  if (parts.length === 3 && parts[0].length === 4) {
    return `${parts[1]}/${parts[2]}/${parts[0]}`
  }
  return val
}

Deno.serve(async (req) => {
  try {
    const supabaseUrl = Deno.env.get('SUPABASE_URL') ?? Deno.env.get('SUPABASE_DB_URL')
    const supabaseKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') ?? Deno.env.get('SUPABASE_ANON_KEY')
    
    if (!supabaseUrl || !supabaseKey) {
      throw new Error("Missing Supabase environment variables.")
    }

    const supabase = createClient(supabaseUrl, supabaseKey)

    console.log("Checking if market is open...")
    const { data: configData } = await supabase
      .from('analysis_config')
      .select('config_value')
      .eq('config_key', 'is_market_open')
      .single()

    if (configData?.config_value !== 'true') {
      console.log("Market is closed. Skipping sync.")
      return new Response(JSON.stringify({ success: true, message: "Market closed. Skipped." }), {
        headers: { "Content-Type": "application/json" },
        status: 200, // Return 200 so cron doesn't fail
      })
    }

    const url = 'https://www.sharesansar.com/mutual-fund-navs'
    const headers = {
      'X-Requested-With': 'XMLHttpRequest',
      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    let allData: any[] = []
    let start = 0
    let length = 50
    
    console.log("Fetching data from ShareSansar...")
    while (true) {
      const response = await fetch(`${url}?draw=1&start=${start}&length=${length}`, { headers })
      if (!response.ok) {
        throw new Error(`ShareSansar returned ${response.status}`)
      }
      const data = await response.json()
      
      if (!data.data || data.data.length === 0) {
        break
      }
        
      allData = allData.concat(data.data)
      
      if (allData.length >= (data.recordsTotal || 0)) {
        break
      }
      
      start += length
    }
    console.log(`Fetched ${allData.length} mutual fund records.`)

    const values = []
    for (const item of allData) {
      const symbol = item.symbol
      if (!symbol) continue;

      values.push({
        symbol: symbol,
        Monthly_Nav: cleanNumeric(item.monthly_nav_price),
        Weekly_Nav: cleanNumeric(item.weekly_nav_price),
        LTP: cleanNumeric(item.close),
        Fund_Size: cleanNumeric(item.fund_size),
        Premium_Discount_Pct: cleanNumeric(item.prem_dis),
        As_Of: convertDate(item.published_date || item.daily_date),
        Weekly_Nav_Date: convertDate(item.weekly_date),
        Mutual_Fund_Name: item.companyname,
        Maturity_Date: convertDate(item.maturity_date),
        Maturity_Period: item.maturity_period,
        Monthly_Nav_Date: item.monthly_date
      })
    }

    console.log("Upserting records into the database...")
    const { data, error } = await supabase
      .from('raw_mf_sharesansar_nav')
      .upsert(values, { onConflict: 'symbol' })

    if (error) {
      throw error
    }

    return new Response(JSON.stringify({ success: true, message: `Successfully synced ${values.length} mutual fund NAVs.` }), {
      headers: { "Content-Type": "application/json" },
      status: 200,
    })
  } catch (error: any) {
    console.error("Sync failed:", error)
    return new Response(JSON.stringify({ success: false, error: error.message }), {
      headers: { "Content-Type": "application/json" },
      status: 500,
    })
  }
})
