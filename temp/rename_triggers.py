import os
import psycopg2
from dotenv import load_dotenv

def get_new_name_and_comment(trigger_name):
    lower_name = trigger_name.lower()
    
    if 'health' in lower_name:
        return 'health_auto', 'Logs sync execution success/failure to sys_script_health table.'
    elif 'updated_at' in lower_name or 'modtime' in lower_name or lower_name.startswith('trg_auto_update_'):
        return 'timestamp_auto', 'Automatically updates the updated_at timestamp on row modification.'
    elif 'pnl' in lower_name:
        return 'pnl_sync', 'Calculates and syncs real-time Profit and Loss to the wiki_profit_loss_analysis table.'
    elif 'mf_analytics' in lower_name or 'portfolio_sync' in lower_name:
        return 'analytics_sync', 'Triggers downstream analytics recalculations.'
    elif 'fk' in lower_name or 'ensure_security' in lower_name:
        return 'fks_ensure', 'Automatically inserts missing foreign keys (e.g. symbols) to prevent constraint violations.'
    elif 'url' in lower_name:
        return 'config_refresh', 'Regenerates URLs or configuration settings based on changes.'
    
    return None, None

def run_migration():
    load_dotenv()
    db_url = os.getenv("DATABASE_URL")
    conn = psycopg2.connect(db_url)
    conn.autocommit = False
    cur = conn.cursor()
    
    query = """
    SELECT event_object_table, trigger_name 
    FROM information_schema.triggers 
    WHERE trigger_schema = 'public'
    AND trigger_name NOT LIKE 'RI_ConstraintTrigger%'
    GROUP BY event_object_table, trigger_name;
    """
    cur.execute(query)
    triggers = cur.fetchall()
    
    rename_count = 0
    table_trigger_counts = {}

    try:
        for table_name, trigger_name in triggers:
            base_new_name, comment = get_new_name_and_comment(trigger_name)
            
            if base_new_name:
                if table_name not in table_trigger_counts:
                    table_trigger_counts[table_name] = {}
                
                new_name = base_new_name
                count = table_trigger_counts[table_name].get(base_new_name, 0)
                if count > 0:
                    new_name = f"{base_new_name}_{count + 1}"
                
                table_trigger_counts[table_name][base_new_name] = count + 1

                if new_name != trigger_name:
                    alter_sql = f'ALTER TRIGGER "{trigger_name}" ON "{table_name}" RENAME TO "{new_name}";'
                    cur.execute(alter_sql)
                    
                    comment_sql = f'COMMENT ON TRIGGER "{new_name}" ON "{table_name}" IS %s;'
                    cur.execute(comment_sql, (comment,))
                    rename_count += 1
                    print(f"Renamed {table_name}.{trigger_name} -> {new_name}")
                elif new_name == trigger_name:
                    comment_sql = f'COMMENT ON TRIGGER "{new_name}" ON "{table_name}" IS %s;'
                    cur.execute(comment_sql, (comment,))
                
        conn.commit()
        print(f"Migration complete. Renamed/commented {rename_count} triggers.")
    except Exception as e:
        conn.rollback()
        print(f"FAILED: {e}")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    run_migration()
