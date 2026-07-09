import os

models_path = "d:/Project/Python/webhook_forwarder/models.py"
with open(models_path, "r", encoding="utf-8") as f:
    content = f.read()

new_model = """
class SystemSetting(Base):
    __tablename__ = "system_settings"

    key = Column(String, primary_key=True, index=True)
    value = Column(String)
"""

if "class SystemSetting" not in content:
    content += "\n" + new_model

with open(models_path, "w", encoding="utf-8") as f:
    f.write(content)
print("Added SystemSetting to models.py")
