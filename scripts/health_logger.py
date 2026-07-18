"""
Helper module providing a function to log script execution statuses to the `sys_script_health` table.
"""

import psycopg2

def log_health(cur, table_name, status, source_page_url=None, script_ran_from=None):
    """
    Logs the execution health of a script to sys_script_health.
    cur: active psycopg2 cursor
    table_name: string name of the target table
    status: string status (e.g., 'SUCCESS', 'FAILED')
    source_page_url: string url of the source data
    script_ran_from: string location where script ran (e.g. 'github_actions', 'windmill')
    """
    try:
        cur.execute("""
            INSERT INTO sys_script_health (table_name, last_run, health_status, source_page_url, script_ran_from)
            VALUES (%s, CURRENT_TIMESTAMP, %s, %s, %s)
            ON CONFLICT (table_name) DO UPDATE SET
                last_run = EXCLUDED.last_run,
                health_status = EXCLUDED.health_status,
                source_page_url = EXCLUDED.source_page_url,
                script_ran_from = EXCLUDED.script_ran_from;
        """, (table_name, status, source_page_url, script_ran_from))
    except Exception as e:
        print(f"Failed to log health for {table_name}: {e}")
