import sqlite3
import os

def migrate():
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "webhook.db")
    print(f"Connecting to database at: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        print("Adding auth_type column to destinations table...")
        cursor.execute("ALTER TABLE destinations ADD COLUMN auth_type VARCHAR DEFAULT 'none'")
        print("Success.")
    except sqlite3.OperationalError as e:
        print(f"Skipped (may already exist): {e}")

    try:
        print("Adding auth_config column to destinations table...")
        cursor.execute("ALTER TABLE destinations ADD COLUMN auth_config VARCHAR NULL")
        print("Success.")
    except sqlite3.OperationalError as e:
        print(f"Skipped (may already exist): {e}")
        
    conn.commit()
    conn.close()
    print("Migration completed successfully.")

if __name__ == "__main__":
    migrate()
