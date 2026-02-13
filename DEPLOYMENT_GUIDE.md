# Deployment & Management Guide

## Quick Start

### 1. Environment Setup
```bash
cp .env.example .env
# Edit .env with your configuration
export $(cat .env | xargs)
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
pip install Flask-Limiter python-dotenv
```

### 3. Initialize Database
```bash
python -c "from database import TokenDatabase; TokenDatabase().init_db()"
```

### 4. Start Application
```bash
python -m app
# Or for development with auto-reload:
python -m flask --app app run --host=0.0.0.0 --port=5001 --debug
```

---

## Module Overview

### config.py
- **Purpose:** Centralized configuration from environment variables
- **Usage:** `from config import API_CONFIG, SECURITY_CONFIG, DATABASE_CONFIG`
- **Key Variables:**
  - `API_CONFIG`: host, port, debug mode
  - `SECURITY_CONFIG`: API keys, encryption keys
  - `RATE_LIMITING_CONFIG`: Rate limit rules
  - `DATABASE_CONFIG`: Database connection settings
  - `LOGGING_CONFIG`: Logger settings
  - `TOKEN_GENERATION_CONFIG`: Token generator parameters

### logger.py
- **Purpose:** Structured logging with rotating file handlers
- **Usage:** `from logger import LoggerSetup; logger = LoggerSetup.setup(); logger.info("message")`
- **Features:**
  - RotatingFileHandler (10MB per file, 10 backups)
  - Console output in development
  - Utility functions: `log_api_request()`, `log_token_generated()`, `log_error_with_context()`
- **Output:** `logs/app.log`

### validation.py
- **Purpose:** Input validation for all user inputs
- **Usage:** `from validation import InputValidator; v = InputValidator(); v.validate_uid("1234567890")`
- **Methods:**
  - `validate_uid(uid)` - 8-10 digits
  - `validate_password(password)` - 8+ characters
  - `validate_server(server)` - BD, IND, BR, US, SAC, NA
  - `validate_token(token)` - JWT format check
  - `validate_api_key(api_key)` - Format validation
  - `validate_url(url)` - URL scheme validation

### database.py
- **Purpose:** SQLite persistence for tokens and metrics
- **Usage:** `from database import TokenDatabase; db = TokenDatabase(); db.init_db()`
- **Tables:**
  - `tokens`: uid, token, server, expiry, created_at
  - `api_logs`: endpoint, method, status_code, response_time, timestamp
  - `token_stats`: server, count, last_refresh, expiry_date
  - `metrics`: metric_name, value, timestamp
- **Key Methods:**
  - `add_token(uid, token, server, expiry_days=1)`
  - `get_valid_tokens(server=None)` - Returns non-expired tokens
  - `delete_expired_tokens()` - Cleanup
  - `log_api_call(endpoint, method, status_code, response_time)`
  - `get_metrics()` - Retrieve performance metrics

### auth.py
- **Purpose:** API key authentication and authorization
- **Usage:** `from auth import require_api_key; @app.route('/endpoint')\n@require_api_key`
- **Decorators:**
  - `@require_api_key` - Requires valid API key
  - `@optional_api_key` - Works with or without API key
  - `@require_admin_key` - Requires admin API key
- **API Key Locations:** Header (X-API-Key), Query (?api_key=), Bearer token

### metrics.py
- **Purpose:** Performance monitoring and health checks
- **Usage:** `from metrics import Metrics; m = Metrics(); m.record_api_call(endpoint, response_time)`
- **Tracked Metrics:**
  - API call count and response times
  - Like sent count per server
  - Token generation rate
  - Token cleanup statistics
  - Error rate and health status
- **Methods:**
  - `record_api_call(endpoint, response_time)`
  - `record_like_sent(server, count)`
  - `record_token_generated(count)`
  - `check_health()` - Returns health status
  - `get_summary()` - Returns all statistics

---

## API Authentication

### Setting API Keys

1. **In .env file:**
   ```
   API_KEYS=sk_live_default
   ADDITIONAL_API_KEYS=sk_live_admin,sk_live_user1
   ADMIN_API_KEY=sk_live_admin
   ```

2. **Generate new API key:**
   ```bash
   python -c "from auth import generate_api_key; print(generate_api_key())"
   ```

### Using API Keys

#### Method 1: Header
```bash
curl -H "X-API-Key: sk_live_admin" http://localhost:5001/admin/metrics
```

#### Method 2: Query String
```bash
curl http://localhost:5001/like?api_key=sk_live_admin&uid=1234567890&server=BD
```

#### Method 3: Bearer Token
```bash
curl -H "Authorization: Bearer sk_live_admin" http://localhost:5001/like
```

---

## Rate Limiting

### Default Limits (per .env)
- `/like` endpoint: 20 requests per hour
- `/refresh_tokens` endpoint: 5 requests per day
- `/token_health` endpoint: 100 requests per hour
- Other endpoints: 200 requests per day

### Customize Rate Limits
Edit `.env`:
```
RATE_LIKE_LIMIT=20 per hour
RATE_REFRESH_LIMIT=5 per day
```

---

## Database Management

### View Tokens
```bash
sqlite3 tokens.db
sqlite> SELECT uid, server, expiry FROM tokens LIMIT 10;
```

### Export Tokens to JSON
```bash
python -c "
from database import TokenDatabase
db = TokenDatabase()
tokens = db.get_valid_tokens()
import json
print(json.dumps(tokens, indent=2))
"
```

### Cleanup Expired Tokens
```bash
python -c "
from database import TokenDatabase
db = TokenDatabase()
deleted = db.delete_expired_tokens()
print(f'Deleted {deleted} expired tokens')
"
```

### View API Logs
```bash
sqlite3 tokens.db "SELECT * FROM api_logs ORDER BY timestamp DESC LIMIT 20;"
```

---

## Monitoring

### Health Check
```bash
curl http://localhost:5001/token_health
```

Response:
```json
{
  "total_tokens": 100,
  "valid_tokens": 95,
  "expired_tokens": 5,
  "tokens_by_server": {"BD": 30, "IND": 35, "BR": 30}
}
```

### Get Metrics (requires admin key)
```bash
curl -H "X-API-Key: sk_live_admin" http://localhost:5001/admin/metrics
```

Response:
```json
{
  "total_api_calls": 1000,
  "total_likes_sent": 5000,
  "total_tokens_generated": 150,
  "avg_response_time": 0.45,
  "error_rate": 0.02,
  "health_status": "healthy"
}
```

---

## Production Deployment

### Vercel (Recommended)
```bash
# vercel.json is already configured
vercel --prod
```

### Docker
```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "-m", "app"]
```

```bash
docker build -t like-api .
docker run -p 5001:5001 --env-file .env like-api
```

### Gunicorn
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5001 app:app
```

---

## Troubleshooting

### Check Logs
```bash
tail -f logs/app.log
```

### Verify Database
```bash
python -c "
from database import TokenDatabase
db = TokenDatabase()
tokens = db.get_valid_tokens()
print(f'Valid tokens: {len(tokens)}')
"
```

### Test API Authentication
```bash
curl -v -H "X-API-Key: sk_live_admin" http://localhost:5001/admin/metrics
```

### Clear Expired Tokens
```bash
python -c "
from database import TokenDatabase
db = TokenDatabase()
deleted = db.delete_expired_tokens()
print(f'Cleaned up {deleted} expired tokens')
"
```

---

## Configuration File Reference

See `.env.example` for all available configuration options.

Key sections:
- **API Configuration:** Host, port, secret key
- **Security:** API keys, encryption keys
- **Rate Limiting:** Request limits per endpoint
- **Database:** SQLite path or MySQL URL
- **Logging:** Log level, file location, rotation settings
- **Token Generation:** Batch size, timeouts, retry settings
- **Monitoring:** Metrics file location, health check interval

---

## Next Steps

1. ✅ Copy `.env.example` to `.env`
2. ✅ Configure environment variables
3. ✅ Run database initialization
4. ✅ Start application
5. ✅ Test API endpoints with curl
6. ✅ Monitor logs and metrics
7. ✅ Deploy to Vercel/Docker/server
