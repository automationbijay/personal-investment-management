import os
import requests
from dotenv import load_dotenv

def trigger_market_depth_sync():
    """
    Triggers the Supabase Edge Function to sync market depth.
    This script can be executed externally via Windows Task Scheduler, n8n, Windmill, etc.
    """
    # Load environment variables from .env
    load_dotenv()
    
    service_role_key = os.environ.get("SERVICE_ROLE_KEY")
    if not service_role_key:
        print("ERROR: SERVICE_ROLE_KEY not found in .env file.")
        return

    # The URL to your deployed Edge Function
    url = "https://isornzmtlnkukfjpemnh.supabase.co/functions/v1/sync-market-depth"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {service_role_key}"
    }

    print("Triggering Market Depth Edge Function...")
    
    try:
        response = requests.post(url, headers=headers)
        
        if response.status_code == 200:
            print("SUCCESS! Edge function executed.")
            print("Response:", response.json())
        else:
            print(f"FAILED with status code: {response.status_code}")
            print("Response:", response.text)
            
    except requests.exceptions.RequestException as e:
        print(f"Network error occurred: {e}")

if __name__ == "__main__":
    trigger_market_depth_sync()
