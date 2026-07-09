from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
import datetime
import uuid
from database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True)
    full_name = Column(String(255), nullable=True)
    hashed_password = Column(String(255))
    
    is_admin = Column(Boolean, default=False)
    is_blocked = Column(Boolean, default=False)
    block_reason = Column(String(255), nullable=True)
    limit_projects = Column(Integer, nullable=True)
    limit_endpoints = Column(Integer, nullable=True)
    limit_logs = Column(Integer, nullable=True)
    
    projects = relationship("Project", back_populates="owner", cascade="all, delete-orphan")

class Project(Base):
    __tablename__ = "projects"
    id = Column(String(255), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    name = Column(String(255), index=True)
    description = Column(String(255), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    owner = relationship("User", back_populates="projects")
    endpoints = relationship("Endpoint", back_populates="project", cascade="all, delete-orphan")
    members = relationship("ProjectMember", back_populates="project", cascade="all, delete-orphan")

class ProjectMember(Base):
    __tablename__ = "project_members"
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(String(255), ForeignKey("projects.id", ondelete="CASCADE"), index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    role = Column(String(255)) # 'viewer', 'editor'
    
    project = relationship("Project", back_populates="members")
    user = relationship("User")

class Endpoint(Base):
    __tablename__ = "endpoints"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True)
    slug = Column(String(255), index=True)
    project_id = Column(String(255), ForeignKey("projects.id"))
    
    is_active = Column(Boolean, default=True)
    
    auth_type = Column(String(255), default="none")
    auth_config = Column(String(255), nullable=True) # JSON string
    
    project = relationship("Project", back_populates="endpoints")
    destinations = relationship("Destination", back_populates="endpoint", cascade="all, delete-orphan")
    logs = relationship("DeliveryLog", back_populates="endpoint", cascade="all, delete-orphan")

class Destination(Base):
    __tablename__ = "destinations"

    id = Column(Integer, primary_key=True, index=True)
    endpoint_id = Column(Integer, ForeignKey("endpoints.id"))
    url = Column(String(255))
    is_active = Column(Boolean, default=True)
    auth_type = Column(String(255), default="none")
    auth_config = Column(String(255), nullable=True) # JSON string

    endpoint = relationship("Endpoint", back_populates="destinations")
    logs = relationship("DeliveryLog", back_populates="destination", cascade="all, delete-orphan")

class DeliveryLog(Base):
    __tablename__ = "delivery_logs"

    id = Column(Integer, primary_key=True, index=True)
    endpoint_id = Column(Integer, ForeignKey("endpoints.id"))
    destination_id = Column(Integer, ForeignKey("destinations.id"), nullable=True)
    
    # Incoming Request Data
    http_method = Column(String(255), default="POST")
    client_ip = Column(String(255), nullable=True)
    headers = Column(Text, nullable=True)
    query_params = Column(Text, nullable=True)
    payload = Column(Text)
    
    # Outgoing / Response Data
    status_code = Column(Integer, nullable=True)
    response_body = Column(Text, nullable=True)
    
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    endpoint = relationship("Endpoint", back_populates="logs")
    destination = relationship("Destination", back_populates="logs")


class SystemSetting(Base):
    __tablename__ = "system_settings"

    key = Column(String(255), primary_key=True, index=True)
    value = Column(String(255))
