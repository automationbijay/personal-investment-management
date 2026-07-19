import * as cheerio from "https://esm.sh/cheerio@1.0.0-rc.12";
import { createClient } from "jsr:@supabase/supabase-js@2";

async function scrapeAshesh() {
  const url = "https://www.ashesh.com.np/gold/widget.php?api=992113q421&header_color=0077e5";
  const response = await fetch(url, {
    headers: { 'User-Agent': 'Mozilla/5.0' }
  });
  
  if (!response.ok) {
      throw new Error(`Failed to fetch Ashesh: ${response.status} ${response.statusText}`);
  }
  
  const html = await response.text();
  const $ = cheerio.load(html);
  const mainDiv = $('.main');

  if (!mainDiv.length) {
    throw new Error("Ashesh: Main container not found");
  }

  const result: any = {};
  const dateDiv = $('.header_date');
  result.date = dateDiv.text().trim() || "Unknown";

  $('.country').each((i, el) => {
    const row = $(el);
    const name = row.find('.name').text().trim();
    const unit = row.find('.unit').text().trim();
    const priceRaw = row.find('.rate_buying').text().trim();
    const priceClean = parseFloat(priceRaw.replace(/[^\d.]/g, '')) || 0;

    const key = `${name}_${unit}`
      .toLowerCase()
      .replace(/\s+/g, '_')
      .replace(/[()]/g, '');
      
    result[key] = priceClean;
  });

  const privacyDiv = $('.privacy');
  const fullNote = privacyDiv.text().trim();
  result.full_note = fullNote;
  
  const updatedMatch = fullNote.match(/Gold & Silver rate updated on\s*(.*?)(?:\.|$)/);
  if (updatedMatch && updatedMatch[1]) {
    result.last_updated_text = updatedMatch[1].trim();
  }
  return result;
}

async function scrapeHamroPatro() {
  const url = "https://www.hamropatro.com/gold";
  const response = await fetch(url, {
    headers: { 'User-Agent': 'Mozilla/5.0' }
  });
  
  if (!response.ok) {
      throw new Error(`Failed to fetch HamroPatro: ${response.status} ${response.statusText}`);
  }
  
  const html = await response.text();
  const $ = cheerio.load(html);
  const result: any = {};

  $('b').each((i, el) => {
    const text = $(el).text();
    if (text.includes('Last Updated')) {
      result.last_updated = text.replace('Last Updated:', '').trim();
      return false; 
    }
  });
  if (!result.last_updated) result.last_updated = "Unknown";

  const lis = $('ul.gold-silver li');
  
  for (let i = 0; i < lis.length; i += 2) {
    if (i + 1 < lis.length) {
      const nameRaw = $(lis[i]).text().trim();
      const priceRaw = $(lis[i+1]).text().trim();
      
      let nameClean = nameRaw.replace(/\s*\(.*?\)/g, '').trim();
      const key = nameClean.toLowerCase()
        .replace(/ - /g, '_')
        .replace(/-/g, '_')
        .replace(/\s+/g, '_');
        
      const priceCleanStr = priceRaw.replace(/[^\d.]/g, '');
      const priceSanitized = priceCleanStr.replace(/^\.+/, '');
      
      result[key] = parseFloat(priceSanitized) || 0;
    }
  }

  return result;
}

Deno.serve(async (req) => {
  try {
    // Run both scrapers in parallel
    const [asheshResult, hamroPatroResult] = await Promise.all([
      scrapeAshesh(),
      scrapeHamroPatro()
    ]);
    
    // Save data to Supabase `analysis_config` table
    const supabaseUrl = Deno.env.get('SUPABASE_URL') as string;
    const supabaseKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') as string;
    const supabase = createClient(supabaseUrl, supabaseKey);

    const { error: dbError } = await supabase
      .from('analysis_config')
      .upsert([
        {
          config_key: 'gold_rates_ashesh',
          config_value: JSON.stringify(asheshResult),
          description: 'Gold & Silver rates scraped from Ashesh.com.np'
        },
        {
          config_key: 'gold_rates_hamrobazar',
          config_value: JSON.stringify(hamroPatroResult),
          description: 'Gold & Silver rates scraped from HamroPatro'
        }
      ]);

    if (dbError) {
      throw new Error(`Database Error: ${dbError.message}`);
    }
    
    return new Response(JSON.stringify({ 
      success: true, 
      saved_to_db: true, 
      data: {
        gold_rates_ashesh: asheshResult,
        gold_rates_hamrobazar: hamroPatroResult
      }
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
