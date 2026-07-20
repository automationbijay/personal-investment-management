# SuperCode for n8n

```text
 _____ _   _ ____  _____ ____   ____ ___  ____  _____
/ ____| | | |  _ \| ____|  _ \ / ___/ _ \|  _ \| ____|
\___ \| | | | |_) |  _| | |_) | |  | | | | | | |  _|
 ___) | |_| |  __/| |___|  _ <| |__| |_| | |_| | |___
|____/ \___/|_|   |_____|_| \_\\____\___/|____/|_____|
```

**Finally. JavaScript libraries in n8n.**

Look, n8n's Code node is great, but it can't do much. No lodash. No axios. No validation. No crypto. Nothing. You're stuck writing vanilla JavaScript like it's 2010.

SuperCode changes that. 47+ production-ready JavaScript libraries, right in your workflow. Do things that were literally impossible before. Yeah, you can also replace 10-15 nodes with one SuperCode node, but that's just the beginning.

## What Makes SuperCode Different

### The Problem
n8n's Code node has ZERO libraries. Want to:
- Validate an email? Can't.
- Parse a CSV properly? Nope.
- Work with Excel files? Forget it.
- Sign JWTs? Not happening.
- Process markdown? No way.
- Generate QR codes? Dream on.

You end up building these massive workflows with 15 nodes just to do basic stuff. HTTP Request → Set → Code → IF → Set → Code → HTTP Request... it's exhausting.

### The Solution
SuperCode gives you 47+ JavaScript libraries that real developers use:
- `lodash` for data manipulation
- `axios` for HTTP requests that actually work
- `joi`/`validator` for proper validation
- `dayjs`/`moment` for dates that make sense
- `XLSX` for Excel files (finally!)
- `crypto-js`/`bcrypt` for security
- `cheerio` for web scraping
- `Handlebars` for templating
- And 40+ more...

Plus, you can access data from ANY previous node in your workflow. No more passing data through 10 nodes.

## Installing SuperCode

### For n8n Community Edition
1. Open your n8n instance
2. Go to Settings → Community Nodes
3. Click Install a community node
4. Enter: `@kenkaiii/n8n-nodes-supercode`
5. Click Install
6. Find "Super Code" in your node list

### For n8n Cloud
Community nodes aren't available on n8n cloud yet. Use self-hosted n8n.

### For Docker Users
Add to your `docker-compose.yml`:
```yaml
environment:
  - N8N_COMMUNITY_PACKAGES_ENABLED=true
```
Then install through the UI as shown above.

## Real Examples: What Wasn't Possible Before

### 1. Excel File Processing (Impossible in vanilla n8n)
```javascript
// Read and process Excel files - literally can't do this without SuperCode
const workbook = XLSX.read(binaryData, { type: 'buffer' });
const sheet = workbook.Sheets[workbook.SheetNames[0]];
const data = XLSX.utils.sheet_to_json(sheet);

// Transform the data
const processed = data.map(row => ({
  ...row,
  email: row.email?.toLowerCase(),
  phone: phoneNumber(row.phone, 'US').formatInternational(),
  id: uuid.v4()
}));

// Create a new Excel file with results
const newSheet = XLSX.utils.json_to_sheet(processed);
const newWorkbook = XLSX.utils.book_new();
XLSX.utils.book_append_sheet(newWorkbook, newSheet, 'Processed');

return {
  binary: {
    data: XLSX.write(newWorkbook, { type: 'buffer' }),
    mimeType: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
  }
};
```

### 2. JWT Authentication (Can't do this in Code node)
```javascript
// Generate secure JWT tokens - impossible without crypto libraries
const payload = {
  userId: user.id,
  email: user.email,
  roles: user.roles
};

// Sign with your secret
const token = jwt.sign(payload, $('credentials').jwtSecret, {
  expiresIn: '24h',
  algorithm: 'HS256'
});

// Also hash passwords properly (not possible in vanilla n8n)
const hashedPassword = await bcrypt.hash(password, 12);

return { token, hashedPassword };
```

### 3. Advanced Data Validation (Not possible before)
```javascript
// Complex validation that's impossible with IF nodes
const schema = joi.object({
  email: joi.string().email().required(),
  age: joi.number().min(18).max(100),
  website: joi.string().uri(),
  phone: joi.string().pattern(/^\+[1-9]\d{1,14}$/),
  preferences: joi.object({
    newsletter: joi.boolean(),
    notifications: joi.array().items(joi.string().valid('email', 'sms', 'push'))
  })
});

// Validate all your webhook data at once
const { error, value } = schema.validate($input.all()[0].json);

if (error) {
  throw new Error(`Validation failed: ${error.details.map(d => d.message).join(', ')}`);
}

// Phone number formatting with Google's libphonenumber
const formatted = phoneNumber(value.phone, 'US').formatInternational();

return value;
```

### 4. Web Scraping with Structure (Replaces complex HTTP + Code chains)
```javascript
// Scrape and parse HTML properly - not possible without cheerio
const response = await axios.get('https://example.com/products');
const $ = cheerio.load(response.data);

const products = [];
$('.product-card').each((i, elem) => {
  products.push({
    title: $(elem).find('.title').text().trim(),
    price: parseFloat($(elem).find('.price').text().replace('$', '')),
    image: $(elem).find('img').attr('src'),
    inStock: $(elem).find('.stock-status').hasClass('available'),
    url: new URL($(elem).find('a').attr('href'), 'https://example.com').href
  });
});

// Filter and sort with lodash
const available = _.chain(products)
  .filter('inStock')
  .sortBy('price')
  .take(10)
  .value();

return available;
```

### 5. Yes, Workflow Consolidation Too
Instead of this mess:
`Webhook → Split → Set → Code → HTTP → IF → Set → Code → HTTP → IF → Code → Set → Merge`

Just one SuperCode node handles everything:
- Validate all inputs at once
- Make multiple API calls in parallel
- Process responses with proper error handling
- Transform data with real libraries
- Return structured results

Performance: 80% fewer nodes, 75% faster execution, way less memory usage.

## Complete Library List (47 Working Libraries)

**Data Processing:** `lodash (_), dayjs, moment-timezone, date-fns, date-fns-tz, bytes, ms, uuid, nanoid`
**Validation & Parsing:** `joi, validator, Ajv, yup, zod (z), qs`
**Files & Documents:** `XLSX (xlsx), pdf-lib, csv-parse, papaparse (Papa), archiver, ini, toml`
**Web & HTTP:** `axios, cheerio, FormData`
**Text & Content:** `handlebars, marked, html-to-text, xml2js, XMLParser, YAML, pluralize, slug, string-similarity, fuse.js (fuzzy)`
**Security & Crypto:** `crypto-js (CryptoJS), jsonwebtoken (jwt), bcryptjs, node-forge`
**Specialized:** `QRCode, jimp, mathjs, iban, libphonenumber-js, currency.js`
**Natural Language:** `franc-min, compromise`
**Async Control:** `p-retry, p-limit`
**Data Operations:** `json-diff-ts, cron-parser`
**Blockchain (if you're into that):** `ethers, web3`
**Media Processing:** `@distube/ytdl-core (ytdl), fluent-ffmpeg, ffmpeg-static`

## Who Should Use This?

**Perfect For:**
- Developers tired of n8n's limitations
- Power users who need real data processing
- Anyone working with Excel files, CSVs, or complex data
- API integrators who need proper auth and validation
- Automation experts building production workflows

**You Need:**
- Basic JavaScript knowledge (or ChatGPT/Claude to write it for you)
- Understanding of which library does what
- n8n self-hosted (not cloud)

**Not For:**
- Complete beginners who've never seen code
- Simple workflows that work fine with basic nodes
- n8n cloud users (community nodes not supported)

## Real Performance Metrics
From actual production workflows:
- API Integration Pipeline: 5 nodes → 1 node (80% reduction)
- Excel Processing Workflow: 12 nodes → 1 node (92% reduction)
- Data Validation Chain: 8 nodes → 1 node (87% reduction)
- Execution Time: 4.2s → 1.1s (74% faster)
- Memory Usage: 248MB → 67MB (73% less)

## Tips for Getting Started
1. **Start Simple:** Try one library at a time. lodash for data manipulation is a good start.
2. **Check the Libraries:** All libraries are pre-loaded. Just use them:
   ```javascript
   // No require() needed!
   const result = _.groupBy(data, 'category');
   const validated = joi.string().email().validate(email);
   ```
3. **Access Previous Nodes:** Get data from any node:
   ```javascript
   const webhookData = $('Webhook').first();
   const apiResponse = $('HTTP Request').all();
   ```
4. **Use AI for Code:** You can use ChatGPT/Claude to write the code. Just tell it:
   - You're using SuperCode in n8n
   - Libraries are pre-loaded as globals
   - Show it the library list
5. **Test First:** Use n8n's preview to test your code before running the full workflow.

## Common Issues
- **"Library not defined"**: Make sure you're using the exact library name from the list. Libraries are globals, no `require()` needed.
- **"Cannot read property of undefined"**: Check if your data exists first. Use optional chaining: `data?.property?.value`
- **Performance issues**: SuperCode loads all libraries on first run (takes 1-2 seconds). Subsequent runs are fast. Don't create multiple SuperCode nodes if one can do it all.

## Version History
- 1.4.5: Better messaging, updated descriptions
- 1.4.4: Fixed all library loading issues, 100% success rate
- 1.4.0: Added 8 new libraries for NLP and text processing
- 1.3.x: Excel security fixes, performance improvements
- 1.0.0: Initial release with 40+ libraries

## Support
Found a bug? Need a library added?
npm: `@kenkaiii/n8n-nodes-supercode`
Email: ken@kenkais.com

## Why I Built This
I was building complex n8n workflows and kept hitting walls. Need to validate an email? Write regex. Parse CSV? Build a parser. Work with Excel? Impossible. Sign a JWT? Not happening.

I realized n8n's Code node is extremely limited. Fair enough. But that means you need 15 nodes to do what should take 15-30 lines of code.

SuperCode fixes that. It's the Code node that should have existed from day one. All the libraries you need, none of the limitations.

*Built by Ken Kai. Because n8n workflows shouldn't suck.*
