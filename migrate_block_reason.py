import sqlite3

def run_migration():
    print("Connecting to webhook.db...")
    conn = sqlite3.connect("webhook.db")
    cursor = conn.cursor()
    
    # Check if block_reason column exists
    cursor.execute("PRAGMA table_info(users)")
    columns = [info[1] for info in cursor.fetchall()]
    
    if "block_reason" not in columns:
        print("Adding block_reason column...")
        cursor.execute("ALTER TABLE users ADD COLUMN block_reason TEXT")
    
    conn.commit()
    conn.close()
    print("Migration completed successfully!")

if __name__ == "__main__":
    run_migration()
