import os
import requests
from dotenv import load_dotenv

load_dotenv()
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

headers = {
    "apikey": key,
    "Authorization": f"Bearer {key}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

# 1. Select
res = requests.get(f"{url}/rest/v1/analysis_config?config_key=eq.is_market_open", headers=headers)
print("SELECT:", res.status_code, res.text)

# 2. Update
update_data = {"config_value": "test"}
res = requests.patch(f"{url}/rest/v1/analysis_config?config_key=eq.is_market_open", headers=headers, json=update_data)
print("UPDATE with eq:", res.status_code, res.text)

# 3. Upsert
res = requests.post(f"{url}/rest/v1/analysis_config", headers=headers, json=[{"config_key": "is_market_open", "config_value": "test"}])
print("INSERT (Post):", res.status_code, res.text)
