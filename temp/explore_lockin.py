import requests
from bs4 import BeautifulSoup
import json

url = "https://www.sharesansar.com/promoter-lockin"
headers = {'User-Agent': 'Mozilla/5.0'}
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, 'html.parser')

table = soup.find('table')
if table:
    headers = [th.text.strip() for th in table.find_all('th')]
    print("HEADERS:", headers)
    
    rows = []
    for tr in table.find('tbody').find_all('tr')[:5]:
        cells = [td.text.strip() for td in tr.find_all('td')]
        rows.append(cells)
    
    print("SAMPLE ROWS:")
    print(json.dumps(rows, indent=2))
else:
    print("No table found in the HTML.")
    
    # Maybe it's ajax? Let's search for ajax endpoints in the script tags
    scripts = soup.find_all('script')
    for script in scripts:
        if script.string and 'ajax' in script.string.lower():
            print("FOUND AJAX IN SCRIPT:")
            print(script.string[:500])
