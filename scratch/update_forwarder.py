import os

forwarder_path = "d:/Project/Python/webhook_forwarder/forwarder.py"
with open(forwarder_path, "r", encoding="utf-8") as f:
    content = f.read()

# Add get_system_setting logic at the top of the file
import_stmt = """import httpx
from sqlalchemy.orm import Session
from database import SessionLocal
import models
from ws_manager import manager"""

if "def get_system_setting" not in content:
    get_setting_func = """
def get_system_setting(db: Session, key: str, default: str):
    setting = db.query(models.SystemSetting).filter(models.SystemSetting.key == key).first()
    if setting:
        return setting.value
    return default
"""
    content = content.replace("from ws_manager import manager", "from ws_manager import manager\n" + get_setting_func)

# Enforce logs limit after db.refresh(log_entry)
old_db_commit = """        db.commit()
        db.refresh(log_entry)
        
        log_dict['id'] = log_entry.id"""

new_db_commit = """        db.commit()
        db.refresh(log_entry)
        
        # Enforce log limits
        try:
            max_logs = int(get_system_setting(db, "max_logs_per_endpoint", "1000"))
            log_count = db.query(models.DeliveryLog).filter(models.DeliveryLog.endpoint_id == endpoint_id).count()
            if log_count > max_logs:
                # Find IDs of oldest logs to delete
                logs_to_delete = log_count - max_logs
                oldest_logs = db.query(models.DeliveryLog.id).filter(
                    models.DeliveryLog.endpoint_id == endpoint_id
                ).order_by(models.DeliveryLog.created_at.asc()).limit(logs_to_delete).all()
                
                if oldest_logs:
                    old_ids = [log[0] for log in oldest_logs]
                    db.query(models.DeliveryLog).filter(models.DeliveryLog.id.in_(old_ids)).delete(synchronize_session=False)
                    db.commit()
        except Exception as e:
            print(f"Error enforcing log limits: {e}")
            db.rollback()
        
        log_dict['id'] = log_entry.id"""

content = content.replace(old_db_commit, new_db_commit)

with open(forwarder_path, "w", encoding="utf-8") as f:
    f.write(content)
print("Updated forwarder.py successfully")
