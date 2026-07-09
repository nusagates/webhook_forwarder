from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime

# Auth Schemas
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)

class UserLogin(BaseModel):
    email: str
    password: str

class UserDeleteRequest(BaseModel):
    password: str

class UserUpdateRequest(BaseModel):
    current_password: str
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    new_password: Optional[str] = None

class User(BaseModel):
    id: int
    email: str
    full_name: Optional[str] = None
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# Destination Schemas
class DestinationBase(BaseModel):
    url: str
    is_active: bool = True
    auth_type: str = "none"
    auth_config: Optional[str] = None

class DestinationCreate(DestinationBase):
    pass

class Destination(DestinationBase):
    id: int
    endpoint_id: int
    class Config:
        from_attributes = True

# Endpoint Schemas
class EndpointCreate(BaseModel):
    name: str
    slug: str
    project_id: str
    auth_type: str = "none"
    auth_config: Optional[str] = None

class Endpoint(BaseModel):
    id: int
    name: str
    slug: str
    project_id: str
    auth_type: str
    auth_config: Optional[str] = None
    destinations: List[Destination] = []
    class Config:
        from_attributes = True

# Project Member Schemas
class ProjectMemberBase(BaseModel):
    role: str

class ProjectMemberCreate(ProjectMemberBase):
    email: EmailStr

class ProjectMember(ProjectMemberBase):
    id: int
    project_id: str
    user_id: int
    user: User
    
    class Config:
        from_attributes = True

# Project Schemas
class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None

class ProjectCreate(ProjectBase):
    pass

class Project(ProjectBase):
    id: str
    user_id: int
    my_role: str = "owner"
    endpoints: List[Endpoint] = []
    members: List[ProjectMember] = []
    class Config:
        from_attributes = True

# Log Schemas
class DeliveryLog(BaseModel):
    id: int
    endpoint_id: int
    destination_id: Optional[int] = None
    http_method: str
    client_ip: Optional[str] = None
    headers: Optional[str] = None
    query_params: Optional[str] = None
    payload: str
    status_code: Optional[int] = None
    response_body: Optional[str] = None
    is_read: bool = False
    created_at: datetime
    class Config:
        from_attributes = True

class PaginatedLogs(BaseModel):
    items: List[DeliveryLog]
    total: int
    page: int
    pages: int
    limit: int


class SystemSettingUpdate(BaseModel):
    max_projects_per_user: int
    max_endpoints_per_project: int
    max_logs_per_endpoint: int


class UserOutAdmin(BaseModel):
    id: int
    email: str
    full_name: Optional[str]
    is_admin: bool
    is_blocked: bool
    block_reason: Optional[str]
    limit_projects: Optional[int]
    limit_endpoints: Optional[int]
    limit_logs: Optional[int]
    
    class Config:
        from_attributes = True

class UserAdminUpdate(BaseModel):
    is_admin: bool
    is_blocked: bool
    block_reason: Optional[str]
    limit_projects: Optional[int] = None
    limit_endpoints: Optional[int] = None
    limit_logs: Optional[int] = None
    limit_destinations: Optional[int] = None
