# API Quick Reference

## Authentication Methods

### 1. Header (Recommended)
```bash
curl -H "X-API-Key: sk_live_admin" http://localhost:5001/endpoint
```

### 2. Query String
```bash
curl "http://localhost:5001/endpoint?api_key=sk_live_admin"
```

### 3. Bearer Token
```bash
curl -H "Authorization: Bearer sk_live_admin" http://localhost:5001/endpoint
```

---

## Public Endpoints (No Auth Required)

### GET /token_health
Check token availability and health status.

**Response:**
```json
{
  "total_tokens": 100,
  "valid_tokens": 95,
  "expired_tokens": 5,
  "tokens_by_server": {
    "BD": 30,
    "IND": 35,
    "BR": 30
  },
  "oldest_token_age_hours": 42,
  "refresh_recommended": false
}
```

**Example:**
```bash
curl http://localhost:5001/token_health
```

---

## Protected Endpoints (API Key Required)

### POST /like
Send likes to one or more profiles.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| uid | string | Yes | User ID (8-10 digits) |
| server | string | Yes | Server: BD, IND, BR, US, SAC, NA |
| token | string | No | Specific token (if not provided, auto-select) |

**Response:**
```json
{
  "status": "success",
  "liked_count": 5,
  "failed_count": 0,
  "timestamp": "2024-02-14T15:30:45Z"
}
```

**Examples:**
```bash
# Auto-select token
curl -H "X-API-Key: sk_live_admin" \
  "http://localhost:5001/like?uid=1234567890&server=BD"

# With specific token
curl -H "X-API-Key: sk_live_admin" \
  "http://localhost:5001/like?uid=1234567890&server=BD&token=xyz123"

# Using POST body
curl -X POST -H "X-API-Key: sk_live_admin" \
  -H "Content-Type: application/json" \
  -d '{"uid": "1234567890", "server": "BD"}' \
  http://localhost:5001/like
```

---

### GET /refresh_tokens
Trigger token refresh for all servers.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| force | boolean | No | Force refresh even if tokens valid |

**Response:**
```json
{
  "status": "success",
  "refreshed_servers": ["BD", "IND", "BR"],
  "new_tokens": 150,
  "timestamp": "2024-02-14T15:30:45Z"
}
```

**Examples:**
```bash
# Normal refresh
curl -H "X-API-Key: sk_live_admin" http://localhost:5001/refresh_tokens

# Force refresh
curl -H "X-API-Key: sk_live_admin" http://localhost:5001/refresh_tokens?force=True
```

---

### GET /refresh_visit_tokens
Refresh visit tokens first, then regular tokens (visit-first strategy).

**Response:**
```json
{
  "status": "success",
  "stage": "completed",
  "visit_tokens_refreshed": 50,
  "regular_tokens_refreshed": 100,
  "timestamp": "2024-02-14T15:30:45Z"
}
```

**Example:**
```bash
curl -H "X-API-Key: sk_live_admin" http://localhost:5001/refresh_visit_tokens
```

---

## Admin Endpoints (Admin Key Required)

### GET /admin/metrics
Get comprehensive metrics and health status.

**Response:**
```json
{
  "total_api_calls": 1000,
  "total_likes_sent": 5000,
  "total_tokens_generated": 150,
  "likes_by_server": {
    "BD": 2000,
    "IND": 2000,
    "BR": 1000
  },
  "avg_response_time": 0.45,
  "error_rate": 0.02,
  "health_status": "healthy",
  "last_token_refresh": "2024-02-14T12:00:00Z",
  "timestamp": "2024-02-14T15:30:45Z"
}
```

**Example:**
```bash
curl -H "X-API-Key: sk_live_admin" http://localhost:5001/admin/metrics
```

---

### POST /admin/cleanup
Manually trigger cleanup of expired tokens.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| server | string | No | Cleanup specific server |

**Response:**
```json
{
  "status": "success",
  "deleted_tokens": 15,
  "remaining_tokens": 85,
  "timestamp": "2024-02-14T15:30:45Z"
}
```

**Examples:**
```bash
# Cleanup all expired tokens
curl -X POST -H "X-API-Key: sk_live_admin" http://localhost:5001/admin/cleanup

# Cleanup specific server
curl -X POST -H "X-API-Key: sk_live_admin" \
  http://localhost:5001/admin/cleanup?server=BD
```

---

### GET /admin/health
Get detailed health and status information.

**Response:**
```json
{
  "uptime_seconds": 3600,
  "total_tokens": 100,
  "valid_tokens": 95,
  "expired_tokens": 5,
  "database_size_mb": 2.5,
  "log_file_size_mb": 0.8,
  "rate_limit_status": "active",
  "notifications_enabled": false,
  "timestamp": "2024-02-14T15:30:45Z"
}
```

**Example:**
```bash
curl -H "X-API-Key: sk_live_admin" http://localhost:5001/admin/health
```

---

## Error Responses

### 400 Bad Request
Validation error or missing required parameters.

```json
{
  "status": "error",
  "code": "VALIDATION_ERROR",
  "message": "UID must be 8-10 digits",
  "errors": {
    "uid": "Invalid UID format"
  }
}
```

### 401 Unauthorized
Missing or invalid API key.

```json
{
  "status": "error",
  "code": "INVALID_API_KEY",
  "message": "API key is missing or invalid"
}
```

### 403 Forbidden
Insufficient permissions (e.g., using regular key on admin endpoint).

```json
{
  "status": "error",
  "code": "PERMISSION_DENIED",
  "message": "This endpoint requires admin API key"
}
```

### 429 Too Many Requests
Rate limit exceeded.

```json
{
  "status": "error",
  "code": "RATE_LIMIT_EXCEEDED",
  "message": "Too many requests. Please try again later.",
  "retry_after_seconds": 3600
}
```

### 500 Internal Server Error
Server error.

```json
{
  "status": "error",
  "code": "INTERNAL_ERROR",
  "message": "An unexpected error occurred",
  "error_id": "err_abc123xyz"
}
```

---

## Valid Values

### Servers
- `BD` - Bangladesh
- `IND` - India
- `BR` - Brazil
- `US` - United States
- `SAC` - South America Central
- `NA` - North America

### HTTP Methods
- `GET` - Read data (GET endpoints)
- `POST` - Create/trigger (POST endpoints)
- `PUT` - Update data (not currently used)
- `DELETE` - Delete data (not currently used)

### Status Codes
- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `429` - Too Many Requests
- `500` - Internal Server Error

---

## Rate Limits

### Default Limits (per minute/hour/day)
- `/like`: 20 per hour
- `/refresh_tokens`: 5 per day
- `/token_health`: 100 per hour
- Admin endpoints: 200 per day
- All other endpoints: 200 per day

### Rate Limit Headers
When you exceed rate limit, response includes:
```
X-RateLimit-Limit: 20
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1707923445
```

---

## Testing Commands

### Test Health (No Auth)
```bash
curl http://localhost:5001/token_health
```

### Test Metrics (Admin Auth)
```bash
curl -H "X-API-Key: sk_live_admin" http://localhost:5001/admin/metrics
```

### Test Like (API Auth)
```bash
curl -H "X-API-Key: sk_live_admin" \
  "http://localhost:5001/like?uid=1234567890&server=BD"
```

### Test Invalid API Key
```bash
curl -H "X-API-Key: invalid_key" http://localhost:5001/admin/metrics
# Should return 401 Unauthorized
```

### Test Rate Limiting
```bash
# Send 21 requests to /like (limit is 20/hour)
for i in {1..21}; do
  curl -H "X-API-Key: sk_live_admin" \
    "http://localhost:5001/like?uid=1234567890&server=BD"
  echo "Request $i"
done
# Last request should return 429 Too Many Requests
```

---

## Advanced Features

### Custom API Key Generation
Generate a new API key programmatically:
```bash
python -c "from auth import generate_api_key; print(generate_api_key())"
```

### Database Query
Access tokens from database:
```bash
python -c "
from database import TokenDatabase
db = TokenDatabase()
tokens = db.get_valid_tokens('BD')
print(f'Valid tokens for BD: {len(tokens)}')
"
```

### View Metrics
Get metrics directly from Python:
```bash
python -c "
from metrics import Metrics
m = Metrics()
print(m.get_summary())
"
```

---

## Webhooks (Future Feature)

Webhooks can be configured to send notifications:
- Token refresh completed
- Token cleanup triggered
- Error threshold exceeded
- Health status changed

Configure in `.env`:
```
NOTIFICATIONS_ENABLED=True
WEBHOOK_URL=https://your-domain.com/webhook
```

---

## Response Time Expectations

| Endpoint | Min | Avg | Max |
|----------|-----|-----|-----|
| /token_health | 10ms | 50ms | 200ms |
| /like | 100ms | 500ms | 2000ms |
| /refresh_tokens | 5000ms | 15000ms | 30000ms |
| /admin/metrics | 50ms | 100ms | 500ms |

---

## Caching

Some responses are cached for performance:
- `/token_health`: Cached for 5 minutes
- `/admin/metrics`: Cached for 1 minute
- Token lists: Cached until refresh

Clear cache by calling refresh endpoints or admin cleanup.

---

## Debugging

### Enable Debug Logging
Set in `.env`:
```
LOG_LEVEL=DEBUG
API_DEBUG=True
```

### Check Logs
```bash
tail -f logs/app.log
```

### Monitor Metrics
```bash
watch curl -H "X-API-Key: sk_live_admin" http://localhost:5001/admin/metrics
```

### Trace Requests
Use curl with verbose flag:
```bash
curl -v -H "X-API-Key: sk_live_admin" http://localhost:5001/admin/metrics
```

---

## Common Workflows

### 1. Check Status and Send Likes
```bash
# Check health
curl http://localhost:5001/token_health

# Send likes if tokens available
curl -H "X-API-Key: sk_live_admin" \
  "http://localhost:5001/like?uid=1234567890&server=BD"

# Check metrics
curl -H "X-API-Key: sk_live_admin" http://localhost:5001/admin/metrics
```

### 2. Refresh Tokens Automatically
```bash
# Trigger refresh
curl -H "X-API-Key: sk_live_admin" http://localhost:5001/refresh_tokens

# Monitor progress
watch curl -H "X-API-Key: sk_live_admin" http://localhost:5001/token_health
```

### 3. System Maintenance
```bash
# Check health
curl -H "X-API-Key: sk_live_admin" http://localhost:5001/admin/health

# Clean up expired tokens
curl -X POST -H "X-API-Key: sk_live_admin" http://localhost:5001/admin/cleanup

# Check metrics again
curl -H "X-API-Key: sk_live_admin" http://localhost:5001/admin/metrics
```

---

## More Information

- **Detailed Setup:** See `SETUP.md`
- **Deployment Guide:** See `DEPLOYMENT_GUIDE.md`
- **Implementation Details:** See `IMPLEMENTATION_CHECKLIST.md`
- **Project Overview:** See `PROJECT_RESEARCH_REPORT.md`
- **Application Logs:** Check `logs/app.log`

---

**Last Updated:** 2024-02-14
**API Version:** 1.0
**Status:** Production Ready
