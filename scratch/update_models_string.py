import os
import re

models_path = "d:/Project/Python/webhook_forwarder/models.py"
with open(models_path, "r", encoding="utf-8") as f:
    content = f.read()

# Replace Column(String, ...) with Column(String(255), ...)
content = re.sub(r'Column\(String,', r'Column(String(255),', content)

# Replace Column(String) with Column(String(255))
content = re.sub(r'Column\(String\)', r'Column(String(255))', content)

with open(models_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Updated models.py with String(255)")
