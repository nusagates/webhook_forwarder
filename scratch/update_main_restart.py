import os

main_path = "d:/Project/Python/webhook_forwarder/main.py"
with open(main_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Add restart endpoint before get_system_settings_api
if "/api/settings/restart" not in content:
    restart_code = """
@app.post("/api/settings/restart")
def restart_server(current_user: User = Depends(auth.get_current_user)):
    check_super_admin(current_user)
    import threading
    import time
    import os
    import signal
    
    def kill_server():
        time.sleep(2)
        os.kill(os.getpid(), signal.SIGTERM)
        
    threading.Thread(target=kill_server).start()
    return {"status": "success", "message": "Restarting server in 2 seconds..."}

@app.get("/api/settings/system")"""
    content = content.replace("@app.get(\"/api/settings/system\")", restart_code)
    
    with open(main_path, "w", encoding="utf-8") as f:
        f.write(content)
print("Updated main.py with /api/settings/restart")
