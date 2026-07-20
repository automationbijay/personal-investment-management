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
        status: 200,
      })
    }

    console.log("Fetching symbols from raw_mf_sharesansar_nav...")
    const { data: symbolsData, error: symbolsError } = await supabase
      .from('raw_mf_sharesansar_nav')
      .select('symbol')

    if (symbolsError) {
      throw symbolsError
    }

    const symbols = symbolsData.map((s: any) => s.symbol)
    console.log(`Found ${symbols.length} symbols to fetch market depth for.`)

    const fetchMarketDepth = async (symbol: string) => {
      let response = await fetch(`https://neps.puribijay.com.np/MarketDepth?symbol=${symbol}`)
      
      if (!response.ok) {
        console.log(`Primary API failed for ${symbol}. Trying alternative endpoint...`)
        response = await fetch(`https://nepse.puribijay.com.np/MarketDepth?symbol=${symbol}`)
        
        if (!response.ok) {
           console.error(`Both primary and alternative APIs failed for ${symbol}.`)
           return null
        }
      }
      
      const data = await response.json()
      
      return {
        symbol,
        total_buy_qty: data.totalBuyQty,
        total_sell_qty: data.totalSellQty,
        buy_market_depth: data.marketDepth?.buyMarketDepthList || [],
        sell_market_depth: data.marketDepth?.sellMarketDepthList || []
      }
    }

    // Chunking to avoid hitting limits too hard
    const CHUNK_SIZE = 5;
    const allRecords = [];
    
    for (let i = 0; i < symbols.length; i += CHUNK_SIZE) {
      const chunk = symbols.slice(i, i + CHUNK_SIZE)
      console.log(`Fetching chunk ${i / CHUNK_SIZE + 1} with symbols: ${chunk.join(', ')}...`)
      
      const promises = chunk.map(symbol => fetchMarketDepth(symbol))
      const results = await Promise.all(promises)
      
      const validRecords = results.filter(r => r !== null)
      allRecords.push(...validRecords)
      
      // small delay between chunks if needed
      await new Promise(resolve => setTimeout(resolve, 500))
    }

    console.log(`Upserting ${allRecords.length} market depth records into the database...`)
    
    if (allRecords.length > 0) {
        const { error: upsertError } = await supabase
          .from('raw_marketdepth_nepseapi_new')
          .upsert(allRecords, { onConflict: 'symbol' })

        if (upsertError) {
          throw upsertError
        }
    }

    return new Response(JSON.stringify({ success: true, message: `Successfully synced ${allRecords.length} market depth records.` }), {
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
