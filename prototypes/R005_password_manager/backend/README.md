# Password Manager Backend

A FastAPI backend for the Password Manager prototype (R005) with JWT authentication and password encryption.

## Features

- **Authentication**: JWT-based user registration and login
- **Password Hashing**: bcrypt for secure password storage
- **Password Encryption**: Fernet symmetric encryption for stored passwords
- **RESTful API**: Complete CRUD operations for password entries
- **User Isolation**: Each user can only access their own password entries

## Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e .
```

## Configuration

Copy `.env.example` to `.env` and update the values:

```bash
cp .env.example .env
```

**Important**: Update `SECRET_KEY` and `ENCRYPTION_KEY` for production!

## Running the Server

```bash
# Using the script
./scripts/run.sh

# Or directly
python -m uvicorn main:app --host 0.0.0.0 --port 8005 --reload
```

The API will be available at `http://localhost:8005`

## API Documentation

Once running, visit:
- Swagger UI: `http://localhost:8005/docs`
- ReDoc: `http://localhost:8005/redoc`

## API Endpoints

### Authentication

- `POST /auth/register` - Register a new user
- `POST /auth/login` - Login and receive access token

### Password Entries (Require JWT token)

- `GET /passwords` - List all password entries (passwords hidden)
- `POST /passwords` - Create a new password entry
- `GET /passwords/{id}` - Get specific entry (password decrypted)
- `PUT /passwords/{id}` - Update a password entry
- `DELETE /passwords/{id}` - Delete a password entry

### Other

- `GET /` - API information
- `GET /health` - Health check

## Testing

```bash
# Using the script
./scripts/test.sh

# Or directly
python -m pytest tests/ -v
```

## Security Notes

### Password Encryption

Passwords are encrypted using Fernet symmetric encryption with PBKDF2 key derivation:
- Master password is used to derive encryption key
- PBKDF2 with SHA256, 100,000 iterations
- 32-byte salt from configuration

**Current Limitation**: The prototype uses a default master password. In production:
- Derive master password from user's login password with additional salt
- Or use per-user encryption keys stored securely

### JWT Tokens

- Tokens expire after 30 minutes (configurable)
- Includes user ID in subject claim
- HMAC-SHA256 signed with SECRET_KEY

### Password Hashing

- User passwords are hashed with bcrypt
- Never stored in plain text
- 12 rounds (passlib default)

## Development

This is a Level 3 prototype demonstrating:
1. JWT authentication patterns
2. Password encryption at rest
3. User-specific data isolation
4. Secure password hashing

For production use, consider:
- Database persistence (PostgreSQL, etc.)
- Per-user encryption keys
- Rate limiting on auth endpoints
- Password strength validation
- Two-factor authentication
- Audit logging
