import os
import re

# Fix Layout.tsx
layout_path = "d:/Project/Python/webhook_forwarder/frontend/src/components/Layout.tsx"
with open(layout_path, "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace("import LogoutIcon from '@mui/icons-material/Logout';", "")
content = content.replace("<Typography textAlign=\"center\">", "<Typography align=\"center\">")
content = content.replace("<Typography textAlign=\"center\" color=\"error\">", "<Typography align=\"center\" color=\"error\">")
content = content.replace("primaryTypographyProps={{ fontSize: '0.9rem' }} ", "")

with open(layout_path, "w", encoding="utf-8") as f:
    f.write(content)

# Fix SystemLimits.tsx
limits_path = "d:/Project/Python/webhook_forwarder/frontend/src/pages/SystemLimits.tsx"
with open(limits_path, "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace("                            inputProps={{ min: 1 }}\n", "")
content = content.replace("                            inputProps={{ min: 10 }}\n", "")

with open(limits_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Fixed TS errors")
