import os

descriptions = {
    "sync_securities.py": "Fetches the master list of all tradable securities from the NEPSE API and upserts them into `raw_securities`.",
    "sync_sharesansar_nav.py": "Scrapes weekly mutual fund NAV data from ShareSansar and upserts it into `raw_mf_sharesansar_nav`.",
    "health_logger.py": "Helper module providing a function to log script execution statuses to the `sys_script_health` table.",
    "setup_health_table.py": "One-off script to create the `sys_script_health` schema for tracking script execution statuses.",
    "backfill_script_health.py": "One-off script that adds `updated_at` columns to legacy raw tables and populates the `sys_script_health` table with their latest timestamps.",
    "setup_auto_updated_at.py": "Enables the `moddatetime` PostgreSQL extension and applies triggers to automatically update `updated_at` columns whenever a row is modified.",
    "alter_health_table.py": "One-off migration script that modified the schema of `sys_script_health` (renaming columns, adding source URL tracking).",
    "remove_redundant_price_history.py": "Cleanup script that deletes records from `raw_price_history` that are older than 60 days to keep the database lean.",
    "update_schema.py": "Migration script that established Primary Keys and Foreign Key relationships between the raw price/NAV tables and `raw_securities`.",
    "setup_price_tables.py": "Initial schema setup script that created the `raw_nepseapi_live_prices` table and the `vw_live_vs_history_price` comparison view.",
    "check_mf_schema.py": "Investigatory script used to explore the schema of existing mutual fund tables.",
    "check_raw_tables.py": "Investigatory script used to list all `raw_` prefixed tables and check for the existence of an `updated_at` column.",
    "test_sharesansar_ajax.py": "Testing script used to analyze the ShareSansar DataTables AJAX payload format during initial scraper development."
}

def add_comments():
    base_dir = r"c:\Users\purib\Desktop\investmetn management supabse db\scripts"
    
    for filename, description in descriptions.items():
        filepath = os.path.join(base_dir, filename)
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # If it already starts with a docstring, skip it
            if not content.startswith('"""'):
                docstring = f'"""\n{description}\n"""\n\n'
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(docstring + content)
                print(f"Added comment to {filename}")
            else:
                print(f"Comment already exists in {filename}")
        else:
            print(f"File not found: {filename}")

if __name__ == "__main__":
    add_comments()
