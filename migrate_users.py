import sqlite3

def run_migration():
    print("Connecting to webhook.db...")
    conn = sqlite3.connect("webhook.db")
    cursor = conn.cursor()
    
    # Check if is_admin column exists
    cursor.execute("PRAGMA table_info(users)")
    columns = [info[1] for info in cursor.fetchall()]
    
    if "is_admin" not in columns:
        print("Adding is_admin column...")
        cursor.execute("ALTER TABLE users ADD COLUMN is_admin BOOLEAN DEFAULT 0")
    
    if "is_blocked" not in columns:
        print("Adding is_blocked column...")
        cursor.execute("ALTER TABLE users ADD COLUMN is_blocked BOOLEAN DEFAULT 0")
        
    if "limit_projects" not in columns:
        print("Adding limit_projects column...")
        cursor.execute("ALTER TABLE users ADD COLUMN limit_projects INTEGER")
        
    if "limit_endpoints" not in columns:
        print("Adding limit_endpoints column...")
        cursor.execute("ALTER TABLE users ADD COLUMN limit_endpoints INTEGER")
        
    if "limit_logs" not in columns:
        print("Adding limit_logs column...")
        cursor.execute("ALTER TABLE users ADD COLUMN limit_logs INTEGER")
        
    # Check endpoints table
    cursor.execute("PRAGMA table_info(endpoints)")
    endpoints_columns = [info[1] for info in cursor.fetchall()]
    if "is_active" not in endpoints_columns:
        print("Adding is_active column to endpoints table...")
        cursor.execute("ALTER TABLE endpoints ADD COLUMN is_active BOOLEAN DEFAULT 1")
    
    conn.commit()
    conn.close()
    print("Migration completed successfully!")

if __name__ == "__main__":
    run_migration()
