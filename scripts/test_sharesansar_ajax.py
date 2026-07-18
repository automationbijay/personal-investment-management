"""
Testing script used to analyze the ShareSansar DataTables AJAX payload format during initial scraper development.
"""

import requests
import json

def fetch_data():
    url = 'https://www.sharesansar.com/mutual-fund-navs'
    headers = {
        'X-Requested-With': 'XMLHttpRequest',
        'User-Agent': 'Mozilla/5.0'
    }
    params = {
        'draw': 1,
        'start': 0,
        'length': 50
    }
    
    response = requests.get(url, headers=headers, params=params)
    data = response.json()
    
    print("Keys in response:", data.keys())
    if 'data' in data and len(data['data']) > 0:
        first_record = data['data'][0]
        print("First record:")
        print(json.dumps(first_record, indent=2))
        
if __name__ == "__main__":
    fetch_data()
