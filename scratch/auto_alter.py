import os

db_path = "d:/Project/Python/webhook_forwarder/database.py"
with open(db_path, "r", encoding="utf-8") as f:
    content = f.read()

auto_alter = """
try:
    from sqlalchemy import text
    with engine.connect() as conn:
        try:
            conn.execute(text("ALTER TABLE users ADD COLUMN limit_destinations INT NULL"))
            conn.commit()
        except:
            pass
except:
    pass
"""

if "ALTER TABLE users ADD COLUMN limit_destinations" not in content:
    content = content.replace("Base = declarative_base()", auto_alter + "\nBase = declarative_base()")
    with open(db_path, "w", encoding="utf-8") as f:
        f.write(content)

print("Added auto schema update for limit_destinations")
