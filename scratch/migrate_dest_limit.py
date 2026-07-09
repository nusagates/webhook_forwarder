from database import SessionLocal, engine
from sqlalchemy import text
import sys

def run_migration():
    try:
        with engine.connect() as conn:
            # Check if column exists
            # SQLite: PRAGMA table_info(users)
            # MySQL: SHOW COLUMNS FROM users LIKE 'limit_destinations'
            if "sqlite" in str(engine.url):
                res = conn.execute(text("PRAGMA table_info(users)")).fetchall()
                cols = [r[1] for r in res]
                if "limit_destinations" not in cols:
                    conn.execute(text("ALTER TABLE users ADD COLUMN limit_destinations INTEGER"))
                    conn.commit()
                    print("Added limit_destinations to SQLite users table.")
            else:
                res = conn.execute(text("SHOW COLUMNS FROM users LIKE 'limit_destinations'")).fetchall()
                if not res:
                    conn.execute(text("ALTER TABLE users ADD COLUMN limit_destinations INT NULL"))
                    conn.commit()
                    print("Added limit_destinations to MySQL users table.")
    except Exception as e:
        print(f"Error: {e}")
        
if __name__ == "__main__":
    run_migration()
