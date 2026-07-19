import * as cheerio from "https://esm.sh/cheerio@1.0.0-rc.12";
import { createClient } from "jsr:@supabase/supabase-js@2";

Deno.serve(async (req) => {
  const url = 'https://www.sharesansar.com/today-share-price';
  
  try {
    const response = await fetch(url, {
      headers: { 'User-Agent': 'Mozilla/5.0' }
    });
    
    if (!response.ok) {
        throw new Error(`Failed to fetch: ${response.status} ${response.statusText}`);
    }
    
    const html = await response.text();
    const $ = cheerio.load(html);
    const shareList: any[] = [];
    const dateStr = new Date().toISOString().split('T')[0];

    // Helper to clean numbers
    const cleanNum = (str: string) => {
        const cleaned = str.replace(/[^\d.-]/g, '');
        return cleaned ? parseFloat(cleaned) : null;
    };

    $('table tbody tr').each((i, row) => {
      const cells = $(row).find('td');
      if (cells.length > 0) {
        const symbol = $(cells[1]).text().trim();
        if (!symbol) return; // Skip if no symbol

        shareList.push({
          symbol: symbol,
          date: dateStr,
          conf: cleanNum($(cells[2]).text().trim()),
          open: cleanNum($(cells[3]).text().trim()),
          high: cleanNum($(cells[4]).text().trim()),
          low: cleanNum($(cells[5]).text().trim()),
          close: cleanNum($(cells[6]).text().trim()),
          ltp: cleanNum($(cells[7]).text().trim()),
          vwap: cleanNum($(cells[10]).text().trim()),
          vol: cleanNum($(cells[11]).text().trim()),
          prev_close: cleanNum($(cells[12]).text().trim()),
          turnover: cleanNum($(cells[13]).text().trim()),
          trans: cleanNum($(cells[14]).text().trim()),
          diff: cleanNum($(cells[15]).text().trim()),
          range: cleanNum($(cells[16]).text().trim()),
          diff_percent: cleanNum($(cells[17]).text().trim()),
          range_percent: cleanNum($(cells[18]).text().trim()),
          vwap_percent: cleanNum($(cells[19]).text().trim()),
          days_120: cleanNum($(cells[20]).text().trim()),
          days_180: cleanNum($(cells[21]).text().trim()),
          weeks_52_high: cleanNum($(cells[22]).text().trim()),
          weeks_52_low: cleanNum($(cells[23]).text().trim())
        });
      }
    });

    if (shareList.length === 0) {
        throw new Error("No data found to scrape.");
    }

    const supabaseUrl = Deno.env.get('SUPABASE_URL') as string;
    const supabaseKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') as string;
    const supabase = createClient(supabaseUrl, supabaseKey);

    const { error: dbError } = await supabase
      .from('raw_sharesansar_daily_price')
      .upsert(shareList, { onConflict: 'symbol, date' });

    if (dbError) {
      throw new Error(`Database Error: ${dbError.message}`);
    }
    
    return new Response(JSON.stringify({ 
      success: true, 
      count: shareList.length 
    }), {
      headers: { "Content-Type": "application/json" },
    });

  } catch (error) {
    return new Response(JSON.stringify({ error: error.message }), {
      status: 500,
      headers: { "Content-Type": "application/json" },
    });
  }
});
