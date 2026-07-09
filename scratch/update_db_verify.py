import os

main_path = "d:/Project/Python/webhook_forwarder/main.py"
with open(main_path, "r", encoding="utf-8") as f:
    content = f.read()

verify_endpoint = """
@app.post("/api/settings/db/verify")
def verify_database_data(config: DbConfig, current_user: User = Depends(auth.get_current_user)):
    check_super_admin(current_user)
    try:
        engine = create_engine(config.url)
        with engine.connect() as conn:
            from sqlalchemy import text
            tables = ['users', 'projects', 'project_members', 'endpoints', 'destinations', 'delivery_logs']
            stats = []
            for table in tables:
                try:
                    result = conn.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
                    stats.append(f"{table}: {result} rows")
                except Exception:
                    stats.append(f"{table}: Table not found or inaccessible")
                    
        return {"status": "success", "message": "Target Database Row Counts:\\n- " + "\\n- ".join(stats)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Verification failed: {str(e)}")

@app.post("/api/settings/db/create")"""

if "/api/settings/db/verify" not in content:
    content = content.replace("@app.post(\"/api/settings/db/create\")", verify_endpoint)
    with open(main_path, "w", encoding="utf-8") as f:
        f.write(content)
print("Added /api/settings/db/verify")
