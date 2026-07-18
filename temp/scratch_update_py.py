import os

scripts_dir = r"c:\Users\purib\Desktop\investmetn management supabse db\scripts"

replacements = {
    '"Symbol"': '"symbol"',
    "'Symbol'": "'symbol'",
    '"Scrip Name"': '"symbol"',
    "'Scrip Name'": "'symbol'",
    '"Scrip"': '"symbol"',
    "'Scrip'": "'symbol'",
    "raw_live_prices": "raw_nepseapi_live_prices",
    "raw_deb_marketdepth": "raw_deb_nepseapi_marketdepth",
    "raw_mf_assets_allocation": "raw_mf_nepsealpha_assets_allocation",
    "raw_deb_nepsealpha": "raw_deb_nepsealpha_details"
}

for filename in os.listdir(scripts_dir):
    if filename.endswith(".py"):
        filepath = os.path.join(scripts_dir, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        for old_str, new_str in replacements.items():
            content = content.replace(old_str, new_str)
            
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Updated {filename}")

print("Python scripts updated.")
