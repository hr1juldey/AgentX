# Redis Architecture for Session Manager

## Storage Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Session Manager API                         │
│                    (FastAPI Backend)                            │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ Connection Attempt
                         │
                    ┌────▼────┐
                    │  Redis  │
                    └────┬────┘
                         │
              ┌──────────┴──────────┐
              │                      │
         ┌────▼────┐          ┌─────▼──────┐
         │ SUCCESS │          │   FAILURE  │
         └────┬────┘          └─────┬──────┘
              │                     │
              │                     │
    ┌─────────▼─────────┐  ┌────────▼────────┐
    │  Redis Storage    │  │  Fallback       │
    │  (Production)     │  │  In-Memory      │
    └───────────────────┘  │  (Development)  │
                          └─────────────────┘
```

## Redis Data Model

### Key Structure

```
Session Data:
  Key: session:{session_id}
  Type: String (JSON)
  TTL: 24 hours (refreshed on access)

User Sessions Index:
  Key: user_sessions:{user_id}
  Type: Set
  Members: [session_id1, session_id2, ...]
  TTL: 24 hours
```

### Example Data

```
# Session Object
session:a1b2c3d4e5f6789
{
  "id": "a1b2c3d4e5f6789",
  "session_token": "xYzAbC123...",
  "user_id": "user_1234567890",
  "device_name": "MacBook Pro",
  "device_type": "desktop",
  "user_agent": "Mozilla/5.0 (Macintosh; ...)",
  "ip_address": "192.168.1.100",
  "created_at": "2026-01-16T10:30:00.000Z",
  "last_active": "2026-01-16T11:45:00.000Z",
  "is_active": true
}

# User's Session Set
user_sessions:user_1234567890
{
  "a1b2c3d4e5f6789",
  "b2c3d4e5f6789a1",
  "c3d4e5f6789a1b2"
}
```

## Redis Operations Flow

### Create Session (Login)

```
Client Request
    │
    ├─ Generate session_id (hex)
    ├─ Generate session_token (url-safe)
    ├─ Create session object
    │
    ▼
Redis Operations
    │
    ├─ SETEX session:{id} 86400 seconds
    │   └─ Store session JSON
    │
    ├─ SADD user_sessions:{user_id} {id}
    │   └─ Add to user's session set
    │
    ├─ EXPIRE user_sessions:{user_id} 86400
    │   └─ Set expiry on index
    │
    ▼
Return SessionResponse
```

### Get Session (Access)

```
Client Request
    │
    ▼
Redis Operations
    │
    ├─ GET session:{id}
    │   └─ Retrieve session JSON
    │
    ├─ Update last_active timestamp
    │
    ├─ SETEX session:{id} 86400 seconds
    │   └─ Refresh TTL (sliding expiration)
    │
    ▼
Return SessionResponse
```

### List Sessions

```
Client Request
    │
    ▼
Redis Operations
    │
    ├─ SMEMBERS user_sessions:{user_id}
    │   └─ Get all session IDs
    │
    ├─ For each session_id:
    │   ├─ GET session:{id}
    │   ├─ Parse JSON
    │   └─ Filter by is_active=true
    │
    ▼
Return SessionListResponse
```

### Delete Session (Logout)

```
Client Request
    │
    ▼
Redis Operations
    │
    ├─ DEL session:{id}
    │   └─ Remove session data
    │
    ├─ SREM user_sessions:{user_id} {id}
    │   └─ Remove from user's set
    │
    ▼
Return 204 No Content
```

### Delete All Sessions (Logout All)

```
Client Request
    │
    ▼
Redis Operations
    │
    ├─ SMEMBERS user_sessions:{user_id}
    │   └─ Get all session IDs
    │
    ├─ For each session_id:
    │   └─ DEL session:{id}
    │
    ├─ DEL user_sessions:{user_id}
    │   └─ Clear user's session set
    │
    ▼
Return 204 No Content
```

## In-Memory Fallback Structure

```
Fallback Storage (dict)
{
  # Session data
  "session:a1b2c3d4": {session object},
  "session:b2c3d4e5": {session object},

  # User session lists
  "user_sessions:user_123": ["a1b2c3d4", "b2c3d4e5"],
  "user_sessions:user_456": ["c3d4e5f6"]
}
```

## Session Lifecycle

```
┌──────────┐
│  Login   │
└─────┬────┘
      │
      ├─ Create session (Redis + Set)
      │
      ▼
┌──────────┐
│  Active  │ ← TTL refreshes on each access
└─────┬────┘
      │
      ├─ Normal access (GET/PUT)
      │  └─ Update last_active
      │  └─ Refresh TTL
      │
      ├─ Logout (DELETE)
      │  └─ Remove from Redis
      │  └─ Remove from user set
      │
      ├─ Session expiry (TTL expires)
      │  └─ Auto-removed by Redis
      │
      ▼
┌──────────┐
│ Expired  │
└──────────┘
```

## Connection Pooling

```
Redis Connection Pool
┌────────────────────────────────────┐
│  Max Connections: 10               │
│  Socket Timeout: 5 seconds         │
│  Connect Timeout: 5 seconds        │
└────────────────────────────────────┘
          │
    ┌─────┼─────┬─────┬─────┐
    │     │     │     │     │
   C1    C2    C3   ...   C10
```

## Key Features

### 1. Graceful Fallback
```
Try Redis → Success → Use Redis
      ↓
   Failure → Use In-Memory + Log Warning
```

### 2. Sliding Expiration
```
Every GET operation:
  - Update last_active
  - Refresh TTL to 24 hours
  - Keep active sessions alive
```

### 3. Automatic Cleanup
```
Redis: Native TTL (automatic)
Memory: Manual cleanup task
```

### 4. Device Fingerprinting
```
Each session stores:
  - device_name (user-provided)
  - device_type (enum)
  - user_agent (browser)
  - ip_address (network)
```

## Performance Considerations

### Redis Advantages
- O(1) key lookup
- O(1) set operations
- Automatic memory management
- Persistence options
- Horizontal scaling (Redis Cluster)

### Fallback Limitations
- Single-server only
- Lost on restart
- Manual cleanup required
- Not production-ready

## Security Features

1. **Secure Token Generation**
   - `secrets.token_urlsafe(64)` - 64 bytes of entropy
   - URL-safe encoding

2. **Session Isolation**
   - Users can only access their own sessions
   - X-User-Id header validation

3. **Automatic Expiry**
   - 24-hour TTL prevents zombie sessions
   - Sliding expiration keeps active sessions

4. **Device Tracking**
   - IP and user-agent logging
   - Helps detect suspicious logins

## Monitoring

### Storage Status Check
```bash
GET /sessions/status/storage
```

### Health Check
```bash
GET /health
```

Both return current storage backend (Redis or Fallback)
