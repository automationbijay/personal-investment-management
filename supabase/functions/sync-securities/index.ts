import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

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

    console.log("Fetching securities from API...")
    let response = await fetch("https://neps.puribijay.com.np/CompanyList")
    
    // Fallback to alternative endpoint if primary is down
    if (!response.ok) {
      console.log(`Primary API failed (${response.status}). Trying alternative endpoint...`)
      response = await fetch("https://nepse.puribijay.com.np/CompanyList")
      
      if (!response.ok) {
        throw new Error(`Both primary and alternative APIs failed. Last error: ${response.status} ${response.statusText}`)
      }
    }
    
    const securities = await response.json()
    console.log(`Fetched ${securities.length} securities.`)

    const values = securities.map((item: any) => ({
      id: item.id,
      symbol: item.symbol,
      security_name: item.securityName,
      name: item.companyName,
      active_status: item.status,
      company_email: item.companyEmail,
      website: item.website,
      sector_name: item.sectorName,
      regulatory_body: item.regulatoryBody,
      instrument_type: item.instrumentType
    }))

    console.log("Upserting records into the database...")
    const { data, error } = await supabase
      .from('raw_securities')
      .upsert(values, { onConflict: 'symbol' })

    if (error) {
      throw error
    }

    return new Response(JSON.stringify({ success: true, message: `Successfully synced ${values.length} securities.` }), {
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
