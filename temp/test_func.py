import os
import requests
from dotenv import load_dotenv

load_dotenv()
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

function_url = f"{url}/functions/v1/check-market-status"
headers = {
    "Authorization": f"Bearer {key}",
    "Content-Type": "application/json"
}

res = requests.post(function_url, headers=headers)
print(res.status_code)
print(res.text)
