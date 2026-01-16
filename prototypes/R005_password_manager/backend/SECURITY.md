# Security Implementation Report

## Authentication & Encryption Implementation

This document details the authentication and encryption implementation for the R005 Password Manager backend.

---

## 1. Authentication System

### 1.1 Password Hashing

**Library**: `passlib` with bcrypt scheme

**Implementation** (`/home/riju279/Documents/Code/XRIG/AgentX/prototypes/R005_password_manager/backend/services/service.py`):

```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
```

**Security Properties**:
- Bcrypt with 12 rounds (passlib default)
- Automatic salt generation
- Passwords never stored in plain text
- Computationally intensive to prevent brute force

### 1.2 JWT Token Authentication

**Implementation**: Custom JWT implementation using HMAC-SHA256

```python
def create_access_token(data: dict) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode.update({"exp": expire})

    import json
    import hmac
    token_data = json.dumps(to_encode)
    signature = hmac.new(
        settings.secret_key.encode(),
        token_data.encode(),
        hashlib.sha256
    ).hexdigest()

    return f"{token_data}.{signature}"

def decode_access_token(token: str) -> Optional[dict]:
    """Decode and verify a JWT access token."""
    # Verify signature and expiration
    # Returns payload if valid, None otherwise
```

**Token Structure**:
- **Header/Payload**: JSON data with user ID and expiration
- **Signature**: HMAC-SHA256 using SECRET_KEY
- **Expiration**: 30 minutes (configurable)
- **Subject (`sub`)**: User ID

**Security Properties**:
- Tokens are signed, not encrypted (standard JWT practice)
- Signature prevents tampering
- Expiration limits token lifetime
- Constant-time comparison for signature verification

---

## 2. Password Encryption System

### 2.1 Encryption Architecture

**Library**: `cryptography` (Fernet symmetric encryption)

**Key Derivation**: PBKDF2 with SHA256

**Implementation** (`/home/riju279/Documents/Code/XRIG/AgentX/prototypes/R005_password_manager/backend/services/service.py`):

```python
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
import base64

def get_encryption_key(master_password: str) -> bytes:
    """Derive an encryption key from a master password using PBKDF2."""
    salt = settings.encryption_key.encode()[:32]
    kdf = PBKDF2(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(master_password.encode()))
    return key

def encrypt_password(plaintext: str, master_password: str) -> str:
    """Encrypt a password using Fernet symmetric encryption."""
    key = get_encryption_key(master_password)
    f = Fernet(key)
    encrypted = f.encrypt(plaintext.encode())
    return base64.urlsafe_b64encode(encrypted).decode()

def decrypt_password(encrypted_password: str, master_password: str) -> str:
    """Decrypt a password that was encrypted with encrypt_password."""
    key = get_encryption_key(master_password)
    f = Fernet(key)
    encrypted_bytes = base64.urlsafe_b64decode(encrypted_password.encode())
    decrypted = f.decrypt(encrypted_bytes)
    return decrypted.decode()
```

### 2.2 Fernet Encryption Properties

**Algorithm**: AES-128 in CBC mode with PKCS7 padding

**Security Properties**:
- **Confidentiality**: AES-128 encryption
- **Integrity**: HMAC-SHA256 authentication
- **Authentication**: Ensures message hasn't been tampered with
- **No Replay**: Timestamp included in token

### 2.3 PBKDF2 Key Derivation

**Parameters**:
- **Algorithm**: SHA256
- **Iterations**: 100,000
- **Key Length**: 32 bytes (256 bits)
- **Salt**: From configuration (32 bytes)

**Security Benefits**:
- Computationally expensive (prevents brute force)
- Derives consistent key from same password
- Salt prevents rainbow table attacks

---

## 3. API Security

### 3.1 Authentication Flow

**Registration** (`POST /auth/register`):
1. Client sends username and password
2. Server validates input
3. Server hashes password with bcrypt
4. Server stores user with hashed password
5. Server returns user ID (without password)

**Login** (`POST /auth/login`):
1. Client sends username and password
2. Server finds user by username
3. Server verifies password with bcrypt
4. If valid, server generates JWT token
5. Server returns token and user data

**Authenticated Requests**:
1. Client includes `Authorization: Bearer <token>` header
2. Server extracts and verifies token signature
3. Server checks token expiration
4. Server extracts user ID from token
5. Server processes request on behalf of user

### 3.2 Authorization

**Implementation** (`/home/riju279/Documents/Code/XRIG/AgentX/prototypes/R005_password_manager/backend/api/routes.py`):

```python
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> UserResponse:
    """Get the currently authenticated user from JWT token."""
    token = credentials.credentials
    token_data = AuthService.decode_access_token(token)

    if token_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    user_id = token_data.get("sub")
    user = UserService.get_user(int(user_id))

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return user
```

**User Isolation**:
- All password entries include `user_id`
- Queries filter by current user's ID
- Users cannot access other users' data
- Explicit 404 errors for cross-user access attempts

---

## 4. Protected Endpoints

### 4.1 Authentication Required

All password endpoints require valid JWT:
- `GET /passwords` - List user's passwords
- `POST /passwords` - Create password entry
- `GET /passwords/{id}` - Get password entry
- `PUT /passwords/{id}` - Update password entry
- `DELETE /passwords/{id}` - Delete password entry

### 4.2 Public Endpoints

No authentication required:
- `GET /` - API information
- `GET /health` - Health check
- `POST /auth/register` - User registration
- `POST /auth/login` - User login

---

## 5. Security Configuration

**File**: `/home/riju279/Documents/Code/XRIG/AgentX/prototypes/R005_password_manager/backend/config/settings.py`

```python
class Settings(BaseSettings):
    app_name: str = "Password Manager"
    port: int = 8005
    debug: bool = True

    # Security
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # Encryption
    encryption_key: str = "your-encryption-key-change-in-production"
```

**Environment**: `/home/riju279/Documents/Code/XRIG/AgentX/prototypes/R005_password_manager/backend/.env`

```env
SECRET_KEY=dev-secret-key-for-testing-only
ENCRYPTION_KEY=dev-encryption-key-32-bytes-long-key
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

---

## 6. Security Considerations

### 6.1 Current Limitations (Prototype)

1. **Master Password**: Uses a default hardcoded master password
   - **Impact**: All encrypted passwords use same key
   - **Fix**: Derive from user's login password or per-user keys

2. **In-Memory Storage**: All data lost on restart
   - **Impact**: No data persistence
   - **Fix**: Add database layer (PostgreSQL, etc.)

3. **Simple JWT**: Custom implementation vs. production libraries
   - **Impact**: May lack some security features
   - **Fix**: Use `python-jose` for production

4. **No Rate Limiting**: Vulnerable to brute force on login
   - **Impact**: Account enumeration possible
   - **Fix**: Add rate limiting middleware

5. **Development Keys**: Default keys in `.env`
   - **Impact**: Predictable if leaked
   - **Fix**: Use environment-specific keys, secrets management

### 6.2 Production Recommendations

1. **Database**: Replace in-memory storage with PostgreSQL
2. **Per-User Encryption Keys**: Derive from user password + unique salt
3. **Proper JWT Library**: Use `python-jose[cryptography]`
4. **Rate Limiting**: Add slowapi or similar
5. **HTTPS**: Enforce TLS in production
6. **Password Strength**: Add zxcvbn or similar validator
7. **Audit Logging**: Log all security events
8. **2FA**: Add two-factor authentication support
9. **Session Management**: Add token revocation/refresh
10. **Input Validation**: Add comprehensive input sanitization

---

## 7. Testing

**Test File**: `/home/riju279/Documents/Code/XRIG/AgentX/prototypes/R005_password_manager/backend/tests/test_api.py`

**Coverage**:
- User registration (success, duplicate username, short password)
- User login (success, invalid credentials)
- Password CRUD operations (create, read, update, delete)
- User isolation (users can't access others' data)
- Authentication required (401 without token)

**Run Tests**:
```bash
cd /home/riju279/Documents/Code/XRIG/AgentX/prototypes/R005_password_manager/backend
./scripts/test.sh
```

---

## 8. Summary

### Authentication Stack
- **Password Hashing**: bcrypt (passlib)
- **Token Format**: JWT (HMAC-SHA256)
- **Token Expiration**: 30 minutes
- **Token Verification**: Signature + expiration check

### Encryption Stack
- **Algorithm**: Fernet (AES-128-CBC + HMAC-SHA256)
- **Key Derivation**: PBKDF2-SHA256 (100k iterations)
- **Key Storage**: Configuration-based (prototype)

### Security Properties
- Passwords hashed at rest (bcrypt)
- Passwords encrypted in storage (Fernet)
- User-specific data isolation
- Token-based authentication
- Expiration-based token invalidation

---

## File Locations

- **Configuration**: `/home/riju279/Documents/Code/XRIG/AgentX/prototypes/R005_password_manager/backend/config/settings.py`
- **Schemas**: `/home/riju279/Documents/Code/XRIG/AgentX/prototypes/R005_password_manager/backend/models/schemas.py`
- **Service Layer**: `/home/riju279/Documents/Code/XRIG/AgentX/prototypes/R005_password_manager/backend/services/service.py`
- **API Routes**: `/home/riju279/Documents/Code/XRIG/AgentX/prototypes/R005_password_manager/backend/api/routes.py`
- **Main App**: `/home/riju279/Documents/Code/XRIG/AgentX/prototypes/R005_password_manager/backend/main.py`
- **Tests**: `/home/riju279/Documents/Code/XRIG/AgentX/prototypes/R005_password_manager/backend/tests/test_api.py`
- **Environment**: `/home/riju279/Documents/Code/XRIG/AgentX/prototypes/R005_password_manager/backend/.env`
- **Documentation**: `/home/riju279/Documents/Code/XRIG/AgentX/prototypes/R005_password_manager/backend/README.md`
