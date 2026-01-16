"""Pydantic schemas for request/response validation."""
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
from enum import Enum
import secrets


class DeviceType(str, Enum):
    """Device type enumeration."""

    desktop = "desktop"
    mobile = "mobile"
    tablet = "tablet"


class SessionBase(BaseModel):
    """Base session schema."""

    device_name: str = Field(..., min_length=1, max_length=100)
    device_type: DeviceType
    user_agent: Optional[str] = Field(None, max_length=500)
    ip_address: Optional[str] = Field(None, max_length=45)  # IPv6 support


class SessionCreate(SessionBase):
    """Schema for creating a new session."""

    pass


class SessionResponse(SessionBase):
    """Schema for session response."""

    id: str
    session_token: str
    user_id: str
    created_at: datetime
    last_active: datetime
    is_active: bool

    class Config:
        from_attributes = True


class SessionUpdate(BaseModel):
    """Schema for updating a session."""

    is_active: bool = Field(..., description="Session active status")


class ErrorResponse(BaseModel):
    """Schema for error responses."""

    error: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class SessionListResponse(BaseModel):
    """Schema for session list response."""

    sessions: list[SessionResponse]
    total: int
    active: int
