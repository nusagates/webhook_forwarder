import os
import re

file_path = "d:/Project/Python/webhook_forwarder/frontend/src/components/Layout.tsx"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Imports
imports = """
import SettingsIcon from '@mui/icons-material/Settings';
import DatabaseSettingsDialog from './DatabaseSettingsDialog';
import { fetchApi } from '../api';
import { useEffect } from 'react';
"""

content = content.replace("import AccountCircleIcon from '@mui/icons-material/AccountCircle';", "import AccountCircleIcon from '@mui/icons-material/AccountCircle';\n" + imports)

# 2. Add state to Layout
states = """
  const [user, setUser] = useState<any>(null);
  const [settingsOpen, setSettingsOpen] = useState(false);

  useEffect(() => {
    fetchApi('/api/users/me').then(data => setUser(data)).catch(() => {});
  }, []);
"""

content = content.replace(
    "  const [open, setOpen] = useState(false);",
    "  const [open, setOpen] = useState(false);\n" + states
)

# 3. Add Settings Button to Toolbar
toolbar_update = """
          <Typography variant="h6" noWrap component="div" sx={{ fontWeight: 600, color: theme.palette.primary.main, flexGrow: 1 }}>
            Webhook Forwarder
          </Typography>
          {user && user.id === 1 && (
            <IconButton color="primary" onClick={() => setSettingsOpen(true)}>
              <SettingsIcon />
            </IconButton>
          )}
"""

content = content.replace(
    """          <Typography variant="h6" noWrap component="div" sx={{ fontWeight: 600, color: theme.palette.primary.main }}>
            Webhook Forwarder
          </Typography>""",
    toolbar_update
)

# 4. Add Dialog Component at the end
dialog_component = """
      </Box>
      <DatabaseSettingsDialog open={settingsOpen} onClose={() => setSettingsOpen(false)} />
    </Box>
  );
}
"""

content = content.replace(
    """      </Box>
    </Box>
  );
}""",
    dialog_component
)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)
print("Updated Layout.tsx successfully")
