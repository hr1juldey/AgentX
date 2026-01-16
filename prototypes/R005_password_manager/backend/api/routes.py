"""API route handlers."""
from typing import List
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from models.schemas import (
    UserCreate,
    UserResponse,
    LoginRequest,
    LoginResponse,
    PasswordEntryCreate,
    PasswordEntryUpdate,
    PasswordEntryResponse,
)
from services.service import (
    AuthService,
    UserService,
    PasswordService,
)

# Router setup
router = APIRouter()
security = HTTPBearer()


# Authentication dependency
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> UserResponse:
    """
    Get the currently authenticated user from JWT token.
    """
    token = credentials.credentials
    token_data = AuthService.decode_access_token(token)

    if token_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    user_id = token_data.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    user = UserService.get_user(int(user_id))
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return user


# Get master password from header (for encryption/decryption)
async def get_master_password() -> str:
    """
    Get master password from custom header.
    In production, this should be derived from user's session or encrypted storage.
    """
    # This is a simplified approach - in production, you'd use a more secure method
    # such as deriving from the user's login password with additional salt
    return "default-master-password"  # Should be passed securely in production


# Auth Routes
@router.post("/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate):
    """
    Register a new user.
    """
    try:
        user = UserService.register(user_data)
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/auth/login", response_model=LoginResponse)
async def login(login_data: LoginRequest):
    """
    Login and receive an access token.
    """
    user = UserService.authenticate(login_data.username, login_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    # Create access token
    token = AuthService.create_access_token({"sub": str(user.id)})

    return LoginResponse(
        access_token=token,
        user=user,
    )


# Password Entry Routes
@router.get("/passwords", response_model=List[PasswordEntryResponse])
async def list_passwords(
    current_user: UserResponse = Depends(get_current_user),
    master_password: str = Depends(get_master_password),
):
    """
    List all password entries for the current user.
    Passwords are hidden by default.
    """
    entries = PasswordService.list_entries(current_user.id, master_password, include_passwords=False)
    return entries


@router.post("/passwords", response_model=PasswordEntryResponse, status_code=status.HTTP_201_CREATED)
async def create_password(
    entry_data: PasswordEntryCreate,
    current_user: UserResponse = Depends(get_current_user),
    master_password: str = Depends(get_master_password),
):
    """
    Create a new password entry.
    The password will be encrypted before storage.
    """
    try:
        entry = PasswordService.create_entry(current_user.id, entry_data, master_password)
        return entry
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/passwords/{entry_id}", response_model=PasswordEntryResponse)
async def get_password(
    entry_id: int,
    current_user: UserResponse = Depends(get_current_user),
    master_password: str = Depends(get_master_password),
):
    """
    Get a specific password entry with decrypted password.
    """
    entry = PasswordService.get_entry(entry_id, current_user.id, master_password)

    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Password entry not found",
        )

    return entry


@router.put("/passwords/{entry_id}", response_model=PasswordEntryResponse)
async def update_password(
    entry_id: int,
    entry_data: PasswordEntryUpdate,
    current_user: UserResponse = Depends(get_current_user),
    master_password: str = Depends(get_master_password),
):
    """
    Update a password entry.
    """
    entry = PasswordService.update_entry(entry_id, current_user.id, entry_data, master_password)

    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Password entry not found",
        )

    return entry


@router.delete("/passwords/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_password(
    entry_id: int,
    current_user: UserResponse = Depends(get_current_user),
):
    """
    Delete a password entry.
    """
    success = PasswordService.delete_entry(entry_id, current_user.id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Password entry not found",
        )

    return None
