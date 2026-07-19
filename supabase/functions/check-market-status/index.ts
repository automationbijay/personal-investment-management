import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

Deno.serve(async (req) => {
  try {
    const supabaseUrl = Deno.env.get('SUPABASE_URL') ?? Deno.env.get('SUPABASE_DB_URL')
    const supabaseKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') ?? Deno.env.get('SUPABASE_ANON_KEY')
    
    if (!supabaseUrl || !supabaseKey) {
      throw new Error("Missing Supabase environment variables.")
    }

    const supabase = createClient(supabaseUrl, supabaseKey)

    console.log("Checking if NEPSE market is open...")
    const response = await fetch("https://nepse.puribijay.com.np/IsNepseOpen")
    if (!response.ok) {
      throw new Error(`API returned ${response.status}: ${response.statusText}`)
    }
    const data = await response.json()
    
    // The API returns "OPEN" or "CLOSE" for isOpen
    const isMarketOpen = (data.isOpen === "OPEN") ? "true" : "false"
    console.log(`Market status: ${data.isOpen} -> mapped to '${isMarketOpen}'`)

    console.log("Saving status to analysis_config...")
    
    // Check if it exists first
    const { data: existing } = await supabase
      .from('analysis_config')
      .select('config_key')
      .eq('config_key', 'is_market_open')
      .maybeSingle()

    let dbError;
    if (existing) {
      const { error } = await supabase
        .from('analysis_config')
        .update({
          config_value: isMarketOpen,
          updated_at: new Date().toISOString()
        })
        .eq('config_key', 'is_market_open')
      dbError = error;
    } else {
      const { error } = await supabase
        .from('analysis_config')
        .insert({
          config_key: 'is_market_open',
          config_value: isMarketOpen,
          description: 'Automatically updated by check-market-status Edge Function based on Nepse API',
          updated_at: new Date().toISOString()
        })
      dbError = error;
    }

    if (dbError) {
      throw dbError
    }

    return new Response(JSON.stringify({ success: true, is_market_open: isMarketOpen }), {
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
