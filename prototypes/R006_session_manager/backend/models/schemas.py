"""
Pydantic schemas for Session Manager API with enhanced Swagger documentation.

This module provides request/response models for session management
and device tracking.
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class DeviceType(str, Enum):
    """Device type enumeration for session tracking.

    Helps categorize user sessions by device form factor.
    """

    DESKTOP = "desktop"
    MOBILE = "mobile"
    TABLET = "tablet"


class SessionBase(BaseModel):
    """Base session schema containing common fields.

    Device identification information for session tracking.
    """

    device_name: str = Field(
        ...,
        description="Human-readable device name",
        min_length=1,
        max_length=100,
        examples=["MacBook Pro", "iPhone 13", "iPad Pro"],
    )
    device_type: DeviceType = Field(
        ...,
        description="Device form factor category",
        examples=[DeviceType.DESKTOP, DeviceType.MOBILE, DeviceType.TABLET],
    )
    user_agent: Optional[str] = Field(
        None,
        description="Browser/user agent string",
        max_length=500,
        examples=["Mozilla/5.0 (Windows NT 10.0; Win64; x64)..."],
    )
    ip_address: Optional[str] = Field(
        None,
        description="Client IP address (IPv4 or IPv6)",
        max_length=45,
        examples=["192.168.1.1", "2001:db8::1"],
    )


class SessionCreate(SessionBase):
    """Schema for creating a new session.

    Register a new device/session for the authenticated user.
    """

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "device_name": "MacBook Pro",
                    "device_type": "desktop",
                    "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)...",
                    "ip_address": "192.168.1.100",
                }
            ]
        }
    }


class SessionResponse(SessionBase):
    """Schema for session response.

    Returns complete session information including tokens.
    """

    id: str = Field(
        ...,
        description="Unique session identifier (UUID)",
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    )
    session_token: str = Field(
        ...,
        description="Session token for authentication",
        examples=["sess_abc123xyz456"],
    )
    user_id: str = Field(
        ..., description="User ID who owns this session", examples=["user_123"]
    )
    created_at: datetime = Field(
        ...,
        description="When the session was created",
        examples=["2024-01-15T10:00:00Z"],
    )
    last_active: datetime = Field(
        ...,
        description="When the session was last active",
        examples=["2024-01-15T14:30:00Z"],
    )
    is_active: bool = Field(
        ...,
        description="Whether the session is currently active",
        examples=[True, False],
    )

    model_config = {"from_attributes": True}


class SessionUpdate(BaseModel):
    """Schema for updating a session.

    Typically used to activate/deactivate sessions.
    """

    is_active: bool = Field(
        ...,
        description="Session active status (true to activate, false to deactivate)",
        examples=[True, False],
    )

    model_config = {"json_schema_extra": {"examples": [{"is_active": False}]}}


class ErrorResponse(BaseModel):
    """Schema for error responses."""

    error: str = Field(
        ...,
        description="Error type",
        examples=["ValidationError", "NotFound", "Unauthorized"],
    )
    detail: Optional[str] = Field(None, description="Additional error details")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="When the error occurred"
    )


class SessionListResponse(BaseModel):
    """Schema for session list response.

    Returns all user sessions with activity statistics.
    """

    sessions: list[SessionResponse] = Field(
        default_factory=list, description="List of sessions (may be empty)"
    )
    total: int = Field(..., description="Total count of sessions", examples=[5])
    active: int = Field(
        ..., description="Count of currently active sessions", examples=[3]
    )
