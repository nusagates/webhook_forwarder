import os
import re

main_path = "d:/Project/Python/webhook_forwarder/main.py"
with open(main_path, "r", encoding="utf-8") as f:
    content = f.read()

switch_code = """
@app.post("/api/settings/db/switch")
def switch_database(config: DbConfig, current_user: User = Depends(auth.get_current_user)):
    check_super_admin(current_user)
    try:
        # Write to .env
        env_file = ".env"
        env_lines = []
        if os.path.exists(env_file):
            with open(env_file, "r") as f:
                env_lines = f.readlines()
                
        found = False
        for i, line in enumerate(env_lines):
            if line.startswith("SQLALCHEMY_DATABASE_URL="):
                env_lines[i] = f"SQLALCHEMY_DATABASE_URL={config.url}\\n"
                found = True
                break
        
        if not found:
            env_lines.append(f"\\nSQLALCHEMY_DATABASE_URL={config.url}\\n")
            
        with open(env_file, "w") as f:
            f.writelines(env_lines)
            
        return {"status": "success", "message": "Database switched successfully! Click Restart Service to apply."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Switch failed: {str(e)}")

@app.post("/api/settings/db/migrate")"""
content = content.replace("@app.post(\"/api/settings/db/migrate\")", switch_code)

with open(main_path, "w", encoding="utf-8") as f:
    f.write(content)

# Now update the Frontend
db_path = "d:/Project/Python/webhook_forwarder/frontend/src/components/DatabaseSettingsDialog.tsx"
with open(db_path, "r", encoding="utf-8") as f:
    content = f.read()

# Add handleSwitch
switch_fn = """    const handleSwitch = async () => {
        if (!await confirm({ message: "Are you sure you want to switch the database? (This does NOT copy data, it only points the app to the new database).", isDanger: true })) return;
        
        const url = buildConnectionString();
        setConsoleOutput({ type: 'info', text: 'Switching database...' });
        try {
            const res = await fetchApi('/api/settings/db/switch', {
                method: 'POST',
                body: JSON.stringify({ url })
            });
            setConsoleOutput({ type: 'success', text: res.message + '\\n\\nPlease click Restart Service to apply changes.' });
        } catch (e: any) {
            setConsoleOutput({ type: 'error', text: e.message || 'Switch failed' });
        }
    };"""

content = content.replace("    const handleMigrate = async () => {", switch_fn + "\n\n    const handleMigrate = async () => {")

# Update buttons
old_buttons = """                <Box>
                    <Button onClick={handleClose} sx={{ mr: 1 }}>Cancel</Button>
                    <Button onClick={handleMigrate} variant="contained" color="warning">Migrate & Save</Button>
                </Box>"""

new_buttons = """                <Box>
                    <Button onClick={handleClose} sx={{ mr: 1 }}>Cancel</Button>
                    {engine !== 'sqlite' && <Button onClick={handleSwitch} variant="outlined" color="primary" sx={{ mr: 1 }}>Save & Switch DB</Button>}
                    <Button onClick={handleMigrate} variant="contained" color="warning">Migrate Data</Button>
                </Box>"""
content = content.replace(old_buttons, new_buttons)

with open(db_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Added DB Switch without migration")
