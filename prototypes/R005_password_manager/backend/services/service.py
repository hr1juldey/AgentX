"""Business logic service layer."""
import base64
import hashlib
from datetime import datetime, timedelta
from typing import Optional, List
import secrets

from passlib.context import CryptContext
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from models.schemas import (
    UserCreate,
    UserResponse,
    PasswordEntryCreate,
    PasswordEntryUpdate,
    PasswordEntryResponse,
)
from config.settings import settings


# Password hashing context (using argon2 instead of bcrypt due to compatibility)
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


# Encryption utilities
def get_encryption_key(master_password: str) -> bytes:
    """
    Derive an encryption key from a master password using PBKDF2.
    """
    # Use the encryption_key from settings as salt
    salt = settings.encryption_key.encode()[:32]
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(master_password.encode()))
    return key


def encrypt_password(plaintext: str, master_password: str) -> str:
    """
    Encrypt a password using Fernet symmetric encryption.
    """
    key = get_encryption_key(master_password)
    f = Fernet(key)
    encrypted = f.encrypt(plaintext.encode())
    return base64.urlsafe_b64encode(encrypted).decode()


def decrypt_password(encrypted_password: str, master_password: str) -> str:
    """
    Decrypt a password that was encrypted with encrypt_password.
    """
    key = get_encryption_key(master_password)
    f = Fernet(key)
    encrypted_bytes = base64.urlsafe_b64decode(encrypted_password.encode())
    decrypted = f.decrypt(encrypted_bytes)
    return decrypted.decode()


# In-memory storage
users_db: dict[int, dict] = {}
password_entries_db: dict[int, dict] = {}
user_id_counter = 0
entry_id_counter = 0


class AuthService:
    """Service for authentication operations."""

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using bcrypt."""
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def create_access_token(data: dict) -> str:
        """Create a JWT access token."""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
        to_encode.update({"exp": expire.timestamp()})  # Convert to timestamp

        # Simple JWT implementation (for production, use python-jose properly)
        import json
        token_data = json.dumps(to_encode)
        # Sign with HMAC using secret key
        import hmac
        signature = hmac.new(
            settings.secret_key.encode(),
            token_data.encode(),
            hashlib.sha256
        ).hexdigest()

        return f"{token_data}|{signature}"

    @staticmethod
    def decode_access_token(token: str) -> Optional[dict]:
        """Decode and verify a JWT access token."""
        try:
            import json
            import hmac

            parts = token.split("|")
            if len(parts) != 2:
                return None

            token_data = parts[0]
            signature = parts[1]

            # Verify signature
            expected_signature = hmac.new(
                settings.secret_key.encode(),
                token_data.encode(),
                hashlib.sha256
            ).hexdigest()

            if not hmac.compare_digest(signature, expected_signature):
                return None

            data = json.loads(token_data)

            # Check expiration
            if datetime.fromtimestamp(data.get("exp", 0), tz=None) < datetime.utcnow():
                return None

            return data
        except Exception:
            return None


class UserService:
    """Service for user management operations."""

    @staticmethod
    def register(user_data: UserCreate) -> UserResponse:
        """Register a new user."""
        global user_id_counter

        # Check if username already exists
        for user in users_db.values():
            if user["username"] == user_data.username:
                raise ValueError("Username already exists")

        user_id_counter += 1
        hashed_password = AuthService.hash_password(user_data.password)

        user = {
            "id": user_id_counter,
            "username": user_data.username,
            "hashed_password": hashed_password,
            "created_at": datetime.utcnow(),
        }

        users_db[user_id_counter] = user
        # Return UserResponse without hashed_password
        return UserResponse(
            id=user["id"],
            username=user["username"],
            created_at=user["created_at"]
        )

    @staticmethod
    def authenticate(username: str, password: str) -> Optional[UserResponse]:
        """Authenticate a user and return user data if valid."""
        for user in users_db.values():
            if user["username"] == username:
                if AuthService.verify_password(password, user["hashed_password"]):
                    # Return UserResponse without hashed_password
                    return UserResponse(
                        id=user["id"],
                        username=user["username"],
                        created_at=user["created_at"]
                    )
                return None
        return None

    @staticmethod
    def get_user(user_id: int) -> Optional[UserResponse]:
        """Get a user by ID."""
        user = users_db.get(user_id)
        if user:
            # Return UserResponse without hashed_password
            return UserResponse(
                id=user["id"],
                username=user["username"],
                created_at=user["created_at"]
            )
        return None


class PasswordService:
    """Service for password entry management operations."""

    @staticmethod
    def create_entry(
        user_id: int,
        entry_data: PasswordEntryCreate,
        master_password: str
    ) -> PasswordEntryResponse:
        """Create a new password entry."""
        global entry_id_counter

        # Verify user exists
        if user_id not in users_db:
            raise ValueError("User not found")

        entry_id_counter += 1

        # Encrypt the password
        encrypted_password = encrypt_password(entry_data.password, master_password)

        entry = {
            "id": entry_id_counter,
            "user_id": user_id,
            "title": entry_data.title,
            "username": entry_data.username,
            "password": encrypted_password,
            "url": entry_data.url,
            "notes": entry_data.notes,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }

        password_entries_db[entry_id_counter] = entry
        return PasswordEntryResponse(**entry)

    @staticmethod
    def list_entries(
        user_id: int,
        master_password: str,
        include_passwords: bool = False
    ) -> List[PasswordEntryResponse]:
        """List all password entries for a user."""
        entries = []

        for entry in password_entries_db.values():
            if entry["user_id"] == user_id:
                entry_copy = entry.copy()
                if include_passwords:
                    try:
                        entry_copy["password"] = decrypt_password(
                            entry["password"],
                            master_password
                        )
                    except Exception:
                        entry_copy["password"] = "[DECRYPTION FAILED]"
                else:
                    entry_copy["password"] = "[HIDDEN]"

                entries.append(PasswordEntryResponse(**entry_copy))

        return entries

    @staticmethod
    def get_entry(
        entry_id: int,
        user_id: int,
        master_password: str
    ) -> Optional[PasswordEntryResponse]:
        """Get a specific password entry."""
        entry = password_entries_db.get(entry_id)

        if not entry or entry["user_id"] != user_id:
            return None

        entry_copy = entry.copy()
        try:
            entry_copy["password"] = decrypt_password(entry["password"], master_password)
        except Exception:
            entry_copy["password"] = "[DECRYPTION FAILED]"

        return PasswordEntryResponse(**entry_copy)

    @staticmethod
    def update_entry(
        entry_id: int,
        user_id: int,
        entry_data: PasswordEntryUpdate,
        master_password: str
    ) -> Optional[PasswordEntryResponse]:
        """Update a password entry."""
        entry = password_entries_db.get(entry_id)

        if not entry or entry["user_id"] != user_id:
            return None

        # Update fields
        if entry_data.title is not None:
            entry["title"] = entry_data.title
        if entry_data.username is not None:
            entry["username"] = entry_data.username
        if entry_data.password is not None:
            entry["password"] = encrypt_password(entry_data.password, master_password)
        if entry_data.url is not None:
            entry["url"] = entry_data.url
        if entry_data.notes is not None:
            entry["notes"] = entry_data.notes

        entry["updated_at"] = datetime.utcnow()

        # Return decrypted version
        entry_copy = entry.copy()
        try:
            entry_copy["password"] = decrypt_password(entry["password"], master_password)
        except Exception:
            entry_copy["password"] = "[DECRYPTION FAILED]"

        return PasswordEntryResponse(**entry_copy)

    @staticmethod
    def delete_entry(entry_id: int, user_id: int) -> bool:
        """Delete a password entry."""
        entry = password_entries_db.get(entry_id)

        if not entry or entry["user_id"] != user_id:
            return False

        del password_entries_db[entry_id]
        return True
