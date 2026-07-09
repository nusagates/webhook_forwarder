import os
import re

db_path = "d:/Project/Python/webhook_forwarder/frontend/src/components/DatabaseSettingsDialog.tsx"
with open(db_path, "r", encoding="utf-8") as f:
    content = f.read()

# Add console output state
if "const [consoleOutput, setConsoleOutput]" not in content:
    content = content.replace("const [currentEngine, setCurrentEngine] = useState('');",
        "const [currentEngine, setCurrentEngine] = useState('');\n    const [consoleOutput, setConsoleOutput] = useState<{ type: 'info' | 'success' | 'error', text: string } | null>(null);")

# Update handleTest
old_test = """    const handleTest = async () => {
        const url = buildConnectionString();
        const tid = toast.loading('Testing connection...');
        try {
            await fetchApi('/api/settings/db/test', {
                method: 'POST',
                body: JSON.stringify({ url })
            });
            toast.success('Connection successful!', { id: tid });
        } catch (e: any) {
            toast.error(e.message || 'Connection failed', { id: tid });
        }
    };"""

new_test = """    const handleTest = async () => {
        const url = buildConnectionString();
        setConsoleOutput({ type: 'info', text: 'Testing connection...' });
        try {
            await fetchApi('/api/settings/db/test', {
                method: 'POST',
                body: JSON.stringify({ url })
            });
            setConsoleOutput({ type: 'success', text: 'Connection successful! Database is reachable.' });
        } catch (e: any) {
            setConsoleOutput({ type: 'error', text: e.message || 'Connection failed' });
        }
    };"""
content = content.replace(old_test, new_test)

# Update handleCreate
old_create = """    const handleCreate = async () => {
        const url = buildConnectionString();
        if (engine === 'sqlite') {
            toast.success("SQLite database is created automatically.");
            return;
        }
        
        const tid = toast.loading('Creating database...');
        try {
            const res = await fetchApi('/api/settings/db/create', {
                method: 'POST',
                body: JSON.stringify({ url })
            });
            toast.success(res.message, { id: tid });
        } catch (e: any) {
            toast.error(e.message || 'Failed to create database', { id: tid });
        }
    };"""

new_create = """    const handleCreate = async () => {
        const url = buildConnectionString();
        if (engine === 'sqlite') {
            setConsoleOutput({ type: 'info', text: 'SQLite database is created automatically.' });
            return;
        }
        
        setConsoleOutput({ type: 'info', text: 'Creating database...' });
        try {
            const res = await fetchApi('/api/settings/db/create', {
                method: 'POST',
                body: JSON.stringify({ url })
            });
            setConsoleOutput({ type: 'success', text: res.message });
        } catch (e: any) {
            setConsoleOutput({ type: 'error', text: e.message || 'Failed to create database' });
        }
    };"""
content = content.replace(old_create, new_create)

# Update handleMigrate
old_migrate = """    const handleMigrate = async () => {
        if (!await confirm({ message: "Are you sure you want to migrate all data to the new database? This process may take a while depending on your log volume.", isDanger: true })) return;
        
        const url = buildConnectionString();
        const tid = toast.loading('Migrating database...');
        try {
            const res = await fetchApi('/api/settings/db/migrate', {
                method: 'POST',
                body: JSON.stringify({ url })
            });
            toast.success(res.message, { id: tid, duration: 8000 });
            onClose();
        } catch (e: any) {
            toast.error(e.message || 'Migration failed', { id: tid, duration: 5000 });
        }
    };"""

new_migrate = """    const handleMigrate = async () => {
        if (!await confirm({ message: "Are you sure you want to migrate all data to the new database? This process may take a while depending on your log volume.", isDanger: true })) return;
        
        const url = buildConnectionString();
        setConsoleOutput({ type: 'info', text: 'Migrating database... Please wait, this might take a while.' });
        try {
            const res = await fetchApi('/api/settings/db/migrate', {
                method: 'POST',
                body: JSON.stringify({ url })
            });
            setConsoleOutput({ type: 'success', text: res.message + '\\n\\nMigration completed successfully. You can close this dialog.' });
        } catch (e: any) {
            setConsoleOutput({ type: 'error', text: e.message || 'Migration failed' });
        }
    };"""
content = content.replace(old_migrate, new_migrate)

# Add console UI block
console_ui = """                {engine !== 'sqlite' && (
                    <>
                        <Box sx={{ display: 'flex', gap: 2 }}>
                            <TextField size="small" label="Host" value={host} onChange={e => setHost(e.target.value)} fullWidth />
                            <TextField size="small" label="Port" value={port} onChange={e => setPort(e.target.value)} placeholder={engine === 'postgresql' ? '5432' : '3306'} sx={{ width: '150px' }} />
                        </Box>
                        <Box sx={{ display: 'flex', gap: 2 }}>
                            <TextField size="small" label="Username" value={user} onChange={e => setUser(e.target.value)} fullWidth />
                            <TextField size="small" label="Password" type="password" value={password} onChange={e => setPassword(e.target.value)} fullWidth />
                        </Box>
                        <TextField size="small" label="Database Name" value={dbName} onChange={e => setDbName(e.target.value)} fullWidth />
                    </>
                )}

                {consoleOutput && (
                    <Box sx={{ 
                        mt: 2, 
                        p: 2, 
                        bgcolor: '#1e1e1e', 
                        color: consoleOutput.type === 'error' ? '#ff6b6b' : consoleOutput.type === 'success' ? '#69db7c' : '#4dabf7', 
                        borderRadius: 1,
                        fontFamily: 'monospace',
                        whiteSpace: 'pre-wrap',
                        wordBreak: 'break-all',
                        maxHeight: '200px',
                        overflowY: 'auto',
                        position: 'relative'
                    }}>
                        <Button 
                            size="small" 
                            sx={{ position: 'absolute', top: 5, right: 5, color: '#fff' }}
                            onClick={() => {
                                navigator.clipboard.writeText(consoleOutput.text);
                                toast.success('Copied to clipboard');
                            }}
                        >
                            Copy
                        </Button>
                        {consoleOutput.text}
                    </Box>
                )}"""

# Replace existing UI part with the new one
old_ui_block = """                {engine !== 'sqlite' && (
                    <>
                        <Box sx={{ display: 'flex', gap: 2 }}>
                            <TextField size="small" label="Host" value={host} onChange={e => setHost(e.target.value)} fullWidth />
                            <TextField size="small" label="Port" value={port} onChange={e => setPort(e.target.value)} placeholder={engine === 'postgresql' ? '5432' : '3306'} sx={{ width: '150px' }} />
                        </Box>
                        <Box sx={{ display: 'flex', gap: 2 }}>
                            <TextField size="small" label="Username" value={user} onChange={e => setUser(e.target.value)} fullWidth />
                            <TextField size="small" label="Password" type="password" value={password} onChange={e => setPassword(e.target.value)} fullWidth />
                        </Box>
                        <TextField size="small" label="Database Name" value={dbName} onChange={e => setDbName(e.target.value)} fullWidth />
                    </>
                )}"""
content = content.replace(old_ui_block, console_ui)

# Update reset logic on close to clear console output
content = content.replace("export default function DatabaseSettingsDialog({ open, onClose }: DatabaseSettingsDialogProps) {", 
    "export default function DatabaseSettingsDialog({ open, onClose }: DatabaseSettingsDialogProps) {\n    const handleClose = () => {\n        setConsoleOutput(null);\n        onClose();\n    };")
content = content.replace("onClose={onClose}", "onClose={handleClose}")
content = content.replace("onClick={onClose}", "onClick={handleClose}")


with open(db_path, "w", encoding="utf-8") as f:
    f.write(content)
print("Updated DatabaseSettingsDialog with console output")
