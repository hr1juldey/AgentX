"""Pydantic schemas for request/response validation."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


# User Schemas
class UserCreate(BaseModel):
    """Schema for user registration."""

    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)


class UserResponse(BaseModel):
    """Schema for user response."""

    id: int
    username: str
    created_at: datetime

    class Config:
        from_attributes = True


# Authentication Schemas
class LoginRequest(BaseModel):
    """Schema for login request."""

    username: str
    password: str


class LoginResponse(BaseModel):
    """Schema for login response."""

    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# Password Entry Schemas
class PasswordEntryBase(BaseModel):
    """Base schema for password entry."""

    title: str = Field(..., min_length=1, max_length=200)
    username: str = Field(..., max_length=100)
    password: str = Field(..., min_length=1)
    url: Optional[str] = Field(None, max_length=500)
    notes: Optional[str] = Field(None, max_length=1000)


class PasswordEntryCreate(PasswordEntryBase):
    """Schema for creating a password entry."""

    pass


class PasswordEntryUpdate(BaseModel):
    """Schema for updating a password entry."""

    title: Optional[str] = Field(None, min_length=1, max_length=200)
    username: Optional[str] = Field(None, max_length=100)
    password: Optional[str] = Field(None, min_length=1)
    url: Optional[str] = Field(None, max_length=500)
    notes: Optional[str] = Field(None, max_length=1000)


class PasswordEntryResponse(PasswordEntryBase):
    """Schema for password entry response."""

    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Error Schemas
class ErrorResponse(BaseModel):
    """Schema for error responses."""

    detail: str
