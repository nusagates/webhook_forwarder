import os

db_path = "d:/Project/Python/webhook_forwarder/frontend/src/components/DatabaseSettingsDialog.tsx"
with open(db_path, "r", encoding="utf-8") as f:
    content = f.read()

# Add handleRestart
if "const handleRestart" not in content:
    restart_fn = """
    const handleRestart = async () => {
        if (!await confirm({ message: "Are you sure you want to restart the backend service? Active webhooks might be dropped during the restart.", isDanger: true })) return;
        
        try {
            const res = await fetchApi('/api/settings/restart', { method: 'POST' });
            setConsoleOutput({ type: 'success', text: res.message + '\\n\\nThe application will reload automatically.' });
            setTimeout(() => {
                window.location.reload();
            }, 3000);
        } catch (e: any) {
            setConsoleOutput({ type: 'error', text: e.message || 'Failed to restart service' });
        }
    };"""
    content = content.replace("const handleMigrate = async () => {", restart_fn + "\n\n    const handleMigrate = async () => {")

# Add button
old_buttons = """                <Box>
                    <Button onClick={handleTest} color="primary" variant="outlined" sx={{ mr: 1 }}>Test Connection</Button>
                    {engine !== 'sqlite' && <Button onClick={handleCreate} color="secondary" variant="outlined">Create DB</Button>}
                </Box>"""

new_buttons = """                <Box>
                    <Button onClick={handleTest} color="primary" variant="outlined" sx={{ mr: 1 }}>Test Connection</Button>
                    {engine !== 'sqlite' && <Button onClick={handleCreate} color="secondary" variant="outlined" sx={{ mr: 1 }}>Create DB</Button>}
                    <Button onClick={handleRestart} color="error" variant="outlined">Restart Service</Button>
                </Box>"""
content = content.replace(old_buttons, new_buttons)

with open(db_path, "w", encoding="utf-8") as f:
    f.write(content)
print("Updated DatabaseSettingsDialog with Restart Button")
