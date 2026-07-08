from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime

# Auth Schemas
class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class User(BaseModel):
    id: int
    email: str
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

# Project Schemas
class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None

class ProjectCreate(ProjectBase):
    pass

class Project(ProjectBase):
    id: str
    user_id: int
    endpoints: List[Endpoint] = []
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
    created_at: datetime
    class Config:
        from_attributes = True
