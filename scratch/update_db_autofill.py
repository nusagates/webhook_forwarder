import os

db_path = "d:/Project/Python/webhook_forwarder/frontend/src/components/DatabaseSettingsDialog.tsx"
with open(db_path, "r", encoding="utf-8") as f:
    content = f.read()

old_load = """    const loadCurrentSettings = async () => {
        try {
            const data = await fetchApi('/api/settings/db');
            setCurrentUrl(data.url);
            setCurrentEngine(data.engine);
        } catch (e: any) {
            toast.error(e.message || "Failed to load database settings");
        }
    };"""

new_load = """    const loadCurrentSettings = async () => {
        try {
            const data = await fetchApi('/api/settings/db');
            setCurrentUrl(data.url);
            setCurrentEngine(data.engine);
            
            if (data.raw_url && data.engine !== 'sqlite') {
                setEngine(data.engine);
                try {
                    const parseUrl = data.raw_url.replace('+pymysql', '');
                    const urlObj = new URL(parseUrl);
                    setHost(urlObj.hostname);
                    setPort(urlObj.port || '');
                    setUser(decodeURIComponent(urlObj.username));
                    setPassword(decodeURIComponent(urlObj.password));
                    setDbName(urlObj.pathname.substring(1));
                } catch (err) {
                    console.error("Failed to parse raw_url", err);
                }
            } else {
                setEngine('sqlite');
            }
        } catch (e: any) {
            toast.error(e.message || "Failed to load database settings");
        }
    };"""

content = content.replace(old_load, new_load)

with open(db_path, "w", encoding="utf-8") as f:
    f.write(content)
print("Updated loadCurrentSettings in DatabaseSettingsDialog.tsx")
