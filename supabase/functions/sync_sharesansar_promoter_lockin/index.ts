import { serve } from 'https://deno.land/std@0.168.0/http/server.ts'
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2.7.1'

const SUPABASE_URL = Deno.env.get('SUPABASE_URL') || ''
const SUPABASE_SERVICE_ROLE_KEY = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') || ''

function cleanNumber(str: string): number | null {
  if (!str || str.trim() === '-' || str.trim() === '') return null;
  const cleaned = str.replace(/,/g, '').replace(/%/g, '').trim();
  const num = parseFloat(cleaned);
  return isNaN(num) ? null : num;
}

function stripHtmlTags(str: string): string {
  if (!str) return '';
  return str.replace(/<[^>]+>/g, '').trim();
}

function parseDate(str: string): string | null {
  if (!str || str.trim() === '-' || str.trim() === '') return null;
  return str.trim();
}

serve(async (req) => {
  try {
    const supabase = createClient(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY);

    console.log("Fetching promoter lock-in data from ShareSansar...");

    const headers = {
      'User-Agent': 'Mozilla/5.0',
      'X-Requested-With': 'XMLHttpRequest',
      'Accept': 'application/json'
    };

    const records = [];

    // type=1 is Locked, type=0 is Unlocked
    for (const type of [1, 0]) {
      const is_locked = (type === 1);

      let start = 0;
      const length = 50; // ShareSansar restricts max length per request
      let hasMore = true;
      let typeRecords = 0;

      // Paginate through all records for this type
      while (hasMore) {
        const url = `https://www.sharesansar.com/promoter-lockin?sector=all&type=${type}&draw=1&start=${start}&length=${length}`;

        const response = await fetch(url, { headers });
        if (!response.ok) {
          throw new Error(`Failed to fetch from sharesansar, status: ${response.status}`);
        }

        const json = await response.json();
        const data = json.data || [];
        typeRecords += data.length;

        for (const row of data) {
          records.push({
            symbol: stripHtmlTags(row.symbol),
            companyname: stripHtmlTags(row.companyname),
            shares: cleanNumber(row.shares),
            prom_share: cleanNumber(row.prom_share),
            public_share: cleanNumber(row.public_share),
            allot_date: parseDate(row.allot_date),
            mf_lock_date: parseDate(row.mf_lock_date),
            prom_lock_date: parseDate(row.prom_lock_date),
            ltp: cleanNumber(row.ltp),
            is_locked: is_locked,
            as_of_date: parseDate(row.date)
          });
        }

        // If we received fewer records than the requested length, we've hit the last page
        if (data.length < length) {
          hasMore = false;
        } else {
          start += length; // Move to the next page
        }
      }
      console.log(`Fetched ${typeRecords} records for type=${type} (is_locked=${is_locked})`);
    }

    console.log(`Total records to upsert: ${records.length}`);

    if (records.length > 0) {
      const { error } = await supabase
        .from('raw_sharesansar_promoter_lockin')
        .upsert(records, { onConflict: 'symbol' });

      if (error) {
        throw error;
      }
    }

    return new Response(JSON.stringify({
      success: true,
      message: `Upserted ${records.length} records into raw_sharesansar_promoter_lockin.`
    }), {
      headers: { "Content-Type": "application/json" }
    });

  } catch (error) {
    console.error("Error syncing promoter lockin:", error);
    return new Response(JSON.stringify({ error: error.message }), {
      status: 500,
      headers: { "Content-Type": "application/json" }
    });
  }
})
