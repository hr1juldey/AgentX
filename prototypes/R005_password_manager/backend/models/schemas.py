"""
Pydantic schemas for Password Manager API with enhanced Swagger documentation.

This module provides request/response models for user authentication
and secure password storage.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    """Schema for user registration.

    Create a new account to store passwords securely.
    """

    username: str = Field(
        ...,
        description="Unique username for account",
        min_length=3,
        max_length=50,
        examples=["john_doe", "user123"]
    )
    password: str = Field(
        ...,
        description="Password (min 6 characters, will be hashed)",
        min_length=6,
        examples=["securePassword123"],
        json_schema_extra={"format": "password"}
    )

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "username": "john_doe",
                "password": "securePassword123"
            }]
        }
    }


class UserResponse(BaseModel):
    """Schema for user response.

    Returns user information (never includes password).
    """

    id: int = Field(
        ...,
        description="Unique user identifier",
        examples=[1, 42]
    )
    username: str = Field(
        ...,
        description="Username",
        examples=["john_doe"]
    )
    created_at: datetime = Field(
        ...,
        description="When the account was created",
        examples=["2024-01-15T10:00:00Z"]
    )

    model_config = {"from_attributes": True}


class LoginRequest(BaseModel):
    """Schema for login request.

    Authenticate with username and password to receive access token.
    """

    username: str = Field(
        ...,
        description="Username",
        examples=["john_doe"]
    )
    password: str = Field(
        ...,
        description="Password",
        examples=["securePassword123"],
        json_schema_extra={"format": "password"}
    )

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "username": "john_doe",
                "password": "securePassword123"
            }]
        }
    }


class LoginResponse(BaseModel):
    """Schema for login response.

    Returns JWT access token and user information.
    """

    access_token: str = Field(
        ...,
        description="JWT access token for authenticated requests",
        examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."]
    )
    token_type: str = Field(
        default="bearer",
        description="Token type (always 'bearer')",
        examples=["bearer"]
    )
    user: UserResponse = Field(
        ...,
        description="Authenticated user information"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "user": {
                    "id": 1,
                    "username": "john_doe",
                    "created_at": "2024-01-15T10:00:00Z"
                }
            }]
        }
    }


class PasswordEntryBase(BaseModel):
    """Base schema for password entry.

    Contains common fields for password storage.
    """

    title: str = Field(
        ...,
        description="Entry title (e.g., 'Gmail Account')",
        min_length=1,
        max_length=200,
        examples=["Gmail Account", "Corporate VPN", "Netflix"]
    )
    username: str = Field(
        ...,
        description="Username or email for the service",
        max_length=100,
        examples=["user@gmail.com", "john.doe"]
    )
    password: str = Field(
        ...,
        description="Password (will be encrypted)",
        min_length=1,
        examples=["MyP@ssw0rd!"],
        json_schema_extra={"format": "password"}
    )
    url: Optional[str] = Field(
        None,
        description="Service URL (optional)",
        max_length=500,
        examples=["https://gmail.com", "https://vpn.company.com"]
    )
    notes: Optional[str] = Field(
        None,
        description="Additional notes (optional)",
        max_length=1000,
        examples=["Security questions: mother's maiden name"]
    )


class PasswordEntryCreate(PasswordEntryBase):
    """Schema for creating a password entry.

    Store a new password securely.
    """

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "title": "Gmail Account",
                "username": "user@gmail.com",
                "password": "MyP@ssw0rd!",
                "url": "https://gmail.com",
                "notes": "Personal email account"
            }]
        }
    }


class PasswordEntryUpdate(BaseModel):
    """Schema for updating a password entry.

    All fields are optional - only include what you want to change.
    """

    title: Optional[str] = Field(
        None,
        description="Updated entry title",
        min_length=1,
        max_length=200
    )
    username: Optional[str] = Field(
        None,
        description="Updated username",
        max_length=100
    )
    password: Optional[str] = Field(
        None,
        description="Updated password",
        min_length=1,
        json_schema_extra={"format": "password"}
    )
    url: Optional[str] = Field(
        None,
        description="Updated service URL",
        max_length=500
    )
    notes: Optional[str] = Field(
        None,
        description="Updated notes",
        max_length=1000
    )


class PasswordEntryResponse(PasswordEntryBase):
    """Schema for password entry response.

    Returns stored password information.
    """

    id: int = Field(
        ...,
        description="Unique entry identifier",
        examples=[1, 42]
    )
    user_id: int = Field(
        ...,
        description="Owner user ID",
        examples=[1]
    )
    created_at: datetime = Field(
        ...,
        description="When the entry was created",
        examples=["2024-01-15T10:00:00Z"]
    )
    updated_at: datetime = Field(
        ...,
        description="When the entry was last updated",
        examples=["2024-01-15T14:30:00Z"]
    )

    model_config = {"from_attributes": True}


class ErrorResponse(BaseModel):
    """Schema for error responses."""

    detail: str = Field(
        ...,
        description="Error message",
        examples=["Invalid credentials", "Entry not found"]
    )
