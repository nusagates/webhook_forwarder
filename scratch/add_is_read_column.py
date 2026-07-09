import sqlite3
import os

def migrate():
    db_path = "webhook.db"
    
    if not os.path.exists(db_path):
        print("Database not found.")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Add is_read column to delivery_logs
        cursor.execute("ALTER TABLE delivery_logs ADD COLUMN is_read BOOLEAN DEFAULT 0")
        print("Migration completed successfully: Added is_read column.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("Column 'is_read' already exists.")
        else:
            print(f"Error during migration: {e}")
            
    conn.commit()
    conn.close()

if __name__ == "__main__":
    migrate()
