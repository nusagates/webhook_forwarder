import os
import re

main_path = "d:/Project/Python/webhook_forwarder/main.py"
with open(main_path, "r", encoding="utf-8") as f:
    content = f.read()

old_block = """                # Expunge from old session and merge to new session
                db.expunge(record)
                from sqlalchemy.orm import make_transient
                make_transient(record)
                new_db.add(record)"""

new_block = """                # Use merge to gracefully handle existing records (updates them instead of duplicate PK error)
                new_db.merge(record)"""

content = content.replace(old_block, new_block)

with open(main_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Updated main.py migration loop to use merge()")
