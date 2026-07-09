import os

main_path = "d:/Project/Python/webhook_forwarder/main.py"
with open(main_path, "r", encoding="utf-8") as f:
    content = f.read()

reactivate_api = """
@app.post("/api/endpoints/{endpoint_id}/reactivate")
def reactivate_endpoint(endpoint_id: int, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    endpoint = db.query(models.Endpoint).filter(models.Endpoint.id == endpoint_id).first()
    if not endpoint:
        raise HTTPException(status_code=404, detail="Endpoint not found")
        
    project, role = get_project_with_role(db, endpoint.project_id, current_user.id)
    if not project or role not in ["owner", "editor"]:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    endpoint.is_active = True
    # Reset rate limit in memory just in case
    if endpoint.slug in RATE_LIMITS:
        RATE_LIMITS[endpoint.slug] = []
        
    db.commit()
    return {"status": "success"}
"""

if "@app.post(\"/api/endpoints/{endpoint_id}/reactivate\")" not in content:
    content = content.replace("if __name__ == \"__main__\":", reactivate_api + "\nif __name__ == \"__main__\":")
    with open(main_path, "w", encoding="utf-8") as f:
        f.write(content)
print("Updated main.py with reactivate API")
