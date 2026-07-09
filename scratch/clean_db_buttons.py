import os

db_path = "d:/Project/Python/webhook_forwarder/frontend/src/components/DatabaseSettingsDialog.tsx"
with open(db_path, "r", encoding="utf-8") as f:
    content = f.read()

# We need to replace the entire <DialogActions> block.
# Let's find it.
import re
pattern = r'<DialogActions[\s\S]*?</DialogActions>'

new_actions = """<DialogActions sx={{ p: 2, display: 'flex', flexDirection: 'column', gap: 2, alignItems: 'stretch', bgcolor: 'background.default' }}>
                {/* Secondary / Utility Tools */}
                <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', justifyContent: 'center', p: 1, border: '1px dashed #ccc', borderRadius: 1 }}>
                    <Button onClick={handleTest} color="primary" variant="outlined" size="small">Test Connection</Button>
                    {engine !== 'sqlite' && <Button onClick={handleVerify} color="info" variant="outlined" size="small">Verify Data</Button>}
                    {engine !== 'sqlite' && <Button onClick={handleCreate} color="secondary" variant="outlined" size="small">Create DB</Button>}
                    <Button onClick={handleRestart} color="error" variant="outlined" size="small">Restart Service</Button>
                </Box>
                
                {/* Primary Actions */}
                <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', justifyContent: 'flex-end' }}>
                    <Button onClick={handleClose} color="inherit" sx={{ minWidth: 100 }}>Cancel</Button>
                    {engine !== 'sqlite' && <Button onClick={handleSwitch} variant="contained" color="primary" sx={{ minWidth: 150 }}>Save & Switch DB</Button>}
                    <Button onClick={handleMigrate} variant="contained" color="warning" sx={{ minWidth: 150 }}>Migrate Data</Button>
                </Box>
            </DialogActions>"""

content = re.sub(pattern, new_actions, content)

with open(db_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Updated DialogActions to be cleaner")
