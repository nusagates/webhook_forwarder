import os

models_path = "d:/Project/Python/webhook_forwarder/models.py"
with open(models_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update User model
old_user_model = """    email = Column(String, unique=True, index=True)
    full_name = Column(String, nullable=True)
    hashed_password = Column(String)
    
    projects = relationship("Project", back_populates="owner", cascade="all, delete-orphan")"""

new_user_model = """    email = Column(String, unique=True, index=True)
    full_name = Column(String, nullable=True)
    hashed_password = Column(String)
    
    is_admin = Column(Boolean, default=False)
    is_blocked = Column(Boolean, default=False)
    limit_projects = Column(Integer, nullable=True)
    limit_endpoints = Column(Integer, nullable=True)
    limit_logs = Column(Integer, nullable=True)
    
    projects = relationship("Project", back_populates="owner", cascade="all, delete-orphan")"""

content = content.replace(old_user_model, new_user_model)

# 2. Update Endpoint model
old_endpoint_model = """    project_id = Column(String, ForeignKey("projects.id"))

    auth_type = Column(String, default="none")"""

new_endpoint_model = """    project_id = Column(String, ForeignKey("projects.id"))
    
    is_active = Column(Boolean, default=True)
    
    auth_type = Column(String, default="none")"""

content = content.replace(old_endpoint_model, new_endpoint_model)

with open(models_path, "w", encoding="utf-8") as f:
    f.write(content)
print("Updated models.py successfully")
