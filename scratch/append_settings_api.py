from pydantic import BaseModel
import os
from sqlalchemy import create_engine
from database import Base, get_db, SQLALCHEMY_DATABASE_URL
from models import User

class DbConfig(BaseModel):
    url: str

def check_super_admin(current_user: User):
    if current_user.id != 1:
        raise HTTPException(status_code=403, detail="Super Admin access required")

@app.get("/api/settings/db")
def get_db_settings(current_user: User = Depends(auth.get_current_user)):
    check_super_admin(current_user)
    
    # mask password if it's not sqlite
    url = SQLALCHEMY_DATABASE_URL
    masked_url = url
    if "://" in url and "@" in url:
        # e.g. postgresql://user:pass@host/db
        parts = url.split("://")
        auth_host = parts[1].split("@")
        if ":" in auth_host[0]:
            user, pw = auth_host[0].split(":", 1)
            masked_url = f"{parts[0]}://{user}:********@{auth_host[1]}"
            
    engine_type = "sqlite"
    if url.startswith("postgres"): engine_type = "postgresql"
    elif url.startswith("mysql"): engine_type = "mysql"
    
    return {
        "engine": engine_type,
        "url": masked_url,
        "raw_url": url # Only for super admin
    }

@app.post("/api/settings/db/test")
def test_db_connection(config: DbConfig, current_user: User = Depends(auth.get_current_user)):
    check_super_admin(current_user)
    try:
        test_engine = create_engine(config.url)
        with test_engine.connect() as conn:
            pass
        return {"status": "success", "message": "Connection successful"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Connection failed: {str(e)}")

@app.post("/api/settings/db/create")
def create_database(config: DbConfig, current_user: User = Depends(auth.get_current_user)):
    check_super_admin(current_user)
    try:
        # Parse URL to get DB name and base URL
        # format: dialect://user:pass@host:port/dbname
        if config.url.startswith("sqlite"):
            return {"status": "success", "message": "SQLite database is a file and will be created automatically."}
            
        base_url, db_name = config.url.rsplit('/', 1)
        
        # Connect to server without db_name (connect to default db 'postgres' or 'mysql')
        if base_url.startswith("postgres"):
            admin_url = base_url + "/postgres"
        else:
            admin_url = base_url # MySQL connects without db
            
        test_engine = create_engine(admin_url, isolation_level="AUTOCOMMIT")
        with test_engine.connect() as conn:
            conn.execute(f"CREATE DATABASE {db_name}")
            
        return {"status": "success", "message": f"Database '{db_name}' created successfully."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create database: {str(e)}")

@app.post("/api/settings/db/migrate")
def migrate_database(config: DbConfig, current_user: User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    check_super_admin(current_user)
    try:
        # 1. Connect to new DB
        new_engine = create_engine(config.url)
        
        # 2. Create tables
        Base.metadata.create_all(new_engine)
        
        # 3. We cannot easily bulk copy using ORM dynamically because we have relationships.
        # But for a simple migration, we can fetch all records and insert them.
        from sqlalchemy.orm import sessionmaker
        NewSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=new_engine)
        new_db = NewSessionLocal()
        
        # In order of foreign key dependencies:
        import models
        tables = [
            models.User,
            models.Project,
            models.ProjectMember,
            models.Endpoint,
            models.Destination,
            models.DeliveryLog
        ]
        
        for table in tables:
            records = db.query(table).all()
            for record in records:
                # Expunge from old session and merge to new session
                db.expunge(record)
                from sqlalchemy.orm import make_transient
                make_transient(record)
                new_db.add(record)
            
            try:
                new_db.commit()
            except Exception as e:
                new_db.rollback()
                raise Exception(f"Failed to migrate table {table.__tablename__}: {str(e)}")
        
        new_db.close()
        
        # 4. Write to .env
        env_file = ".env"
        env_lines = []
        if os.path.exists(env_file):
            with open(env_file, "r") as f:
                env_lines = f.readlines()
                
        # Update or add SQLALCHEMY_DATABASE_URL
        found = False
        for i, line in enumerate(env_lines):
            if line.startswith("SQLALCHEMY_DATABASE_URL="):
                env_lines[i] = f"SQLALCHEMY_DATABASE_URL={config.url}\n"
                found = True
                break
        
        if not found:
            env_lines.append(f"\nSQLALCHEMY_DATABASE_URL={config.url}\n")
            
        with open(env_file, "w") as f:
            f.writelines(env_lines)
            
        return {"status": "success", "message": "Migration completed successfully. Please restart the backend service."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Migration failed: {str(e)}")
