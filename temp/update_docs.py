import os
import glob

docs_dir = r"c:\Users\purib\Desktop\investmetn management supabse db\docs"

# 1. Rename files
rename_map = {
    "average_table.md": "wiki_average_table.md",
    "vw_mf_summary_analytics.md": "view_mf_summary_analytics.md",
    "mf_assets_value_change.md": "view_mf_assets_value_change.md",
    "mf_ask_bid.md": "view_mf_ask_bid.md",
    "deb_ytm_analysis.md": "view_deb_ytm_analysis.md"
}

for root, dirs, files in os.walk(docs_dir):
    for file in files:
        if file in rename_map:
            old_path = os.path.join(root, file)
            new_path = os.path.join(root, rename_map[file])
            os.rename(old_path, new_path)
            print(f"Renamed {old_path} to {new_path}")

# 2. Replace content inside all markdown files
replace_map = {
    "vw_mf_summary_analytics": "view_mf_summary_analytics",
    "mf_assets_value_change": "view_mf_assets_value_change",
    "mf_ask_bid": "view_mf_ask_bid",
    "deb_ytm_analysis": "view_deb_ytm_analysis",
    "`average` table": "`wiki_average` table",
    "average_table.md": "wiki_average_table.md",
    "public.average": "public.wiki_average"
}

for root, dirs, files in os.walk(docs_dir):
    for file in files:
        if file.endswith(".md"):
            filepath = os.path.join(root, file)
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            
            new_content = content
            for old, new in replace_map.items():
                new_content = new_content.replace(old, new)
                
            if new_content != content:
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(new_content)
                print(f"Updated content in {filepath}")

print("Done updating docs.")
