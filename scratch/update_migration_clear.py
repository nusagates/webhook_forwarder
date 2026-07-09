import os

main_path = "d:/Project/Python/webhook_forwarder/main.py"
with open(main_path, "r", encoding="utf-8") as f:
    content = f.read()

# Add truncation block
truncation_code = """        # In order of foreign key dependencies:
        import models
        tables = [
            models.User,
            models.Project,
            models.ProjectMember,
            models.Endpoint,
            models.Destination,
            models.DeliveryLog
        ]
        
        # 3. Clear target database to avoid IntegrityError (Duplicate primary keys)
        for table in reversed(tables):
            try:
                new_db.execute(table.__table__.delete())
            except Exception:
                pass
        new_db.commit()"""

content = content.replace("        # In order of foreign key dependencies:\n        import models\n        tables = [\n            models.User,\n            models.Project,\n            models.ProjectMember,\n            models.Endpoint,\n            models.Destination,\n            models.DeliveryLog\n        ]", truncation_code)

# Revert merge to make_transient + add
old_merge = """                # Use merge to gracefully handle existing records (updates them instead of duplicate PK error)
                new_db.merge(record)"""

new_add = """                # Expunge from old session and add to new session
                db.expunge(record)
                from sqlalchemy.orm import make_transient
                make_transient(record)
                new_db.add(record)"""

content = content.replace(old_merge, new_add)

with open(main_path, "w", encoding="utf-8") as f:
    f.write(content)
print("Updated main.py with truncation and make_transient")
