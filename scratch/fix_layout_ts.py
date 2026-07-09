import os

layout_path = "d:/Project/Python/webhook_forwarder/frontend/src/components/Layout.tsx"
with open(layout_path, "r", encoding="utf-8") as f:
    content = f.read()

# Remove unused imports
content = content.replace("import Select from '@mui/material/Select';\nimport FormControl from '@mui/material/FormControl';\nimport InputLabel from '@mui/material/InputLabel';\n", "")

# Fix PaperProps TS error
content = content.replace("PaperProps={{ sx: { width: 220, maxHeight: 300 } }}", "sx={{ '& .MuiPaper-root': { width: 220, maxHeight: 300 } }}")

with open(layout_path, "w", encoding="utf-8") as f:
    f.write(content)
print("Fixed TS errors in Layout.tsx")
