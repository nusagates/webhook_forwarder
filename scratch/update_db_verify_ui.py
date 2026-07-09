import os

db_path = "d:/Project/Python/webhook_forwarder/frontend/src/components/DatabaseSettingsDialog.tsx"
with open(db_path, "r", encoding="utf-8") as f:
    content = f.read()

# Add handleVerify
verify_fn = """    const handleVerify = async () => {
        const url = buildConnectionString();
        setConsoleOutput({ type: 'info', text: 'Verifying data on target database...' });
        try {
            const res = await fetchApi('/api/settings/db/verify', {
                method: 'POST',
                body: JSON.stringify({ url })
            });
            setConsoleOutput({ type: 'success', text: res.message });
        } catch (e: any) {
            setConsoleOutput({ type: 'error', text: e.message || 'Verification failed' });
        }
    };"""

if "const handleVerify" not in content:
    content = content.replace("    const handleTest = async () => {", verify_fn + "\n\n    const handleTest = async () => {")

# Update buttons to include Verify Data
old_buttons = """                <Box>
                    <Button onClick={handleTest} color="primary" variant="outlined" sx={{ mr: 1 }}>Test Connection</Button>
                    {engine !== 'sqlite' && <Button onClick={handleCreate} color="secondary" variant="outlined" sx={{ mr: 1 }}>Create DB</Button>}
                    <Button onClick={handleRestart} color="error" variant="outlined">Restart Service</Button>
                </Box>"""

new_buttons = """                <Box>
                    <Button onClick={handleTest} color="primary" variant="outlined" sx={{ mr: 1 }}>Test Connection</Button>
                    {engine !== 'sqlite' && <Button onClick={handleVerify} color="info" variant="outlined" sx={{ mr: 1 }}>Verify Data</Button>}
                    {engine !== 'sqlite' && <Button onClick={handleCreate} color="secondary" variant="outlined" sx={{ mr: 1 }}>Create DB</Button>}
                    <Button onClick={handleRestart} color="error" variant="outlined">Restart Service</Button>
                </Box>"""

content = content.replace(old_buttons, new_buttons)

with open(db_path, "w", encoding="utf-8") as f:
    f.write(content)
print("Updated DatabaseSettingsDialog with Verify Button")
