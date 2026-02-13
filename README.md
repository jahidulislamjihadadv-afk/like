# 🎯 Like Project - Production-Ready API

Complete Free Fire token management and like-sending API with automatic token refresh, comprehensive logging, input validation, authentication, metrics tracking, and database persistence.

## ✨ Features

- ✅ **Token Management:** Auto-refresh, expiry detection, cleanup
- ✅ **API Authentication:** API key-based (header, query, bearer token)
- ✅ **Input Validation:** UID, server, token, API key validation
- ✅ **Database Persistence:** SQLite for tokens, API logs, metrics
- ✅ **Metrics & Monitoring:** Real-time health checks, performance tracking
- ✅ **Rate Limiting:** Protected endpoints with request limits
- ✅ **Comprehensive Logging:** File rotation, debug info, error tracking
- ✅ **Scheduled Tasks:** Automatic token refresh every 2 hours
- ✅ **Admin Panel:** Metrics, health status, manual cleanup
- ✅ **Deployment Ready:** Vercel, Docker, Gunicorn compatible

## 📁 Project Structure

```
like/
├── app.py                          # Main Flask API server (1,386 lines)
├── config.py                       # Configuration management
├── logger.py                       # Logging system with file rotation
├── validation.py                   # Input validation (UID, server, token, etc)
├── database.py                     # SQLite database layer
├── auth.py                         # API key authentication & decorators
├── metrics.py                      # Performance metrics & monitoring
│
├── token_generator/                # Token generation engine
│   ├── token_gen.py                # Core generator with parallel processing
│   ├── menu.py                     # Batch mode interface
│   ├── credentials.txt             # Account credentials
│   └── requirements.txt
│
├── templates/                      # Web UI
│   └── index.html
│
├── tests/                          # Test suite (to be created)
│   ├── test_validation.py
│   ├── test_auth.py
│   └── test_database.py
│
├── logs/                           # Application logs (auto-created)
│   └── app.log                     # Rotating log file
│
├── tokens.db                       # SQLite database (auto-created)
│
├── .env.example                    # Environment configuration template
├── .env                            # Environment configuration (create from .env.example)
├── .gitignore                      # Git ignore rules
├── requirements.txt                # Python dependencies
├── vercel.json                     # Vercel deployment config
│
├── SETUP.md                        # Step-by-step setup guide
├── DEPLOYMENT_GUIDE.md             # Deployment instructions
├── API_REFERENCE.md                # Complete API documentation
├── IMPLEMENTATION_CHECKLIST.md     # Integration checklist for app.py
├── PROJECT_RESEARCH_REPORT.md      # Detailed architecture & improvements
│
└── .github/
    └── workflows/
        └── ci-cd.yml               # GitHub Actions CI/CD pipeline
```

## 🚀 Quick Start

### 1. Clone Repository
```bash
git clone https://github.com/jahidulislamjihadadv-afk/like.git
cd like
```

### 2. Setup Environment
```bash
cp .env.example .env
# Edit .env with your configuration
pip install -r requirements.txt
```

### 3. Initialize Database
```bash
python -c "from database import TokenDatabase; TokenDatabase().init_db()"
```

### 4. Test Modules
```bash
python test_modules.py
```

### 5. Start Application
```bash
python -m app
# Or with debug mode:
python -m flask --app app run --host=0.0.0.0 --port=5001 --debug
```

### 6. Test API
```bash
# Public endpoint (no auth required)
curl http://localhost:5001/token_health

# Protected endpoint (requires API key)
curl -H "X-API-Key: sk_live_admin" http://localhost:5001/admin/metrics
```

## 📚 Documentation

- **[SETUP.md](SETUP.md)** - Detailed setup instructions with troubleshooting
- **[API_REFERENCE.md](API_REFERENCE.md)** - Complete API endpoint documentation
- **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)** - Deployment & management guide
- **[IMPLEMENTATION_CHECKLIST.md](IMPLEMENTATION_CHECKLIST.md)** - app.py integration checklist
- **[PROJECT_RESEARCH_REPORT.md](PROJECT_RESEARCH_REPORT.md)** - Architecture & improvements

## 🔑 Key Endpoints

| Endpoint | Method | Auth | Purpose |
|----------|--------|------|---------|
| `/token_health` | GET | No | Token availability check |
| `/like` | GET/POST | API Key | Send likes to profile |
| `/refresh_tokens` | GET | API Key | Manual token refresh |
| `/refresh_visit_tokens` | GET | API Key | Visit-first token refresh |
| `/admin/metrics` | GET | Admin | Performance metrics |
| `/admin/health` | GET | Admin | System health info |
| `/admin/cleanup` | POST | Admin | Manual token cleanup |

## 🔐 Authentication

### API Key Methods

**Option 1: Header**
```bash
curl -H "X-API-Key: sk_live_admin" http://localhost:5001/endpoint
```

**Option 2: Query String**
```bash
curl "http://localhost:5001/endpoint?api_key=sk_live_admin"
```

**Option 3: Bearer Token**
```bash
curl -H "Authorization: Bearer sk_live_admin" http://localhost:5001/endpoint
```

### Environment Setup
```bash
# .env file
API_KEYS=sk_live_default
ADMIN_API_KEY=sk_live_admin
```

## 📊 Modules Overview

### `config.py` (118 lines)
Centralized configuration management from environment variables.
- API configuration (host, port, debug)
- Security settings (API keys, encryption)
- Rate limiting rules
- Database configuration
- Logging settings
- Token generation parameters

### `logger.py` (76 lines)
Comprehensive logging with rotating file handlers.
- Console + file output
- RotatingFileHandler (10MB per file, 10 backups)
- Utility functions for common logging scenarios

### `validation.py` (151 lines)
Input validation for all user inputs.
- UID validation (8-10 digits)
- Server validation (BD, IND, BR, US, SAC, NA)
- Token format validation
- API key validation
- URL validation

### `database.py` (268 lines)
SQLite persistence layer with 4 tables.
- `tokens` table: uid, token, server, expiry, created_at
- `api_logs` table: endpoint, method, status_code, response_time, timestamp
- `token_stats` table: server, count, last_refresh, expiry_date
- `metrics` table: metric_name, value, timestamp

### `auth.py` (113 lines)
API key authentication and authorization.
- AuthManager class for key validation
- `@require_api_key` decorator
- `@optional_api_key` decorator
- `@require_admin_key` decorator
- API key generation utility

### `metrics.py` (128 lines)
Performance monitoring and health tracking.
- API call tracking
- Like sent statistics
- Token generation metrics
- Error rate monitoring
- Health status checking

## ⚙️ Configuration

All configuration is managed through `.env` file (see [SETUP.md](SETUP.md)):

```bash
# API Configuration
API_HOST=0.0.0.0
API_PORT=5001
SECRET_KEY=your-secret-key

# Security
API_KEYS=sk_live_default
ADMIN_API_KEY=sk_live_admin
ENCRYPTION_KEY=Yg&tc%DEuh6%Zc^8
ENCRYPTION_IV=6oyZDr22E3ychjM%

# Rate Limiting
RATE_LIKE_LIMIT=20 per hour
RATE_REFRESH_LIMIT=5 per day

# Database
DB_TYPE=sqlite
DB_SQLITE_PATH=tokens.db

# Logging
LOG_LEVEL=INFO
LOG_FILE=app.log

# Scheduling
SCHEDULER_REFRESH_HOURS=2
```

## 🛠️ Development

### Run Tests
```bash
python test_modules.py    # Quick module test
pytest tests/             # Full test suite (to be created)
```

### Check Logs
```bash
tail -f logs/app.log
```

### Monitor Metrics
```bash
curl -H "X-API-Key: sk_live_admin" http://localhost:5001/admin/metrics
```

### Database Operations
```bash
# View tables
sqlite3 tokens.db ".tables"

# Count tokens
sqlite3 tokens.db "SELECT COUNT(*) FROM tokens;"

# View recent API logs
sqlite3 tokens.db "SELECT * FROM api_logs ORDER BY timestamp DESC LIMIT 10;"
```

## 🐳 Docker Deployment

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

## 🚀 Vercel Deployment

```bash
vercel --prod
```

Configuration is in `vercel.json`

## 📈 Monitoring

### Health Check
```bash
curl http://localhost:5001/token_health
```

### Get Metrics (Admin)
```bash
curl -H "X-API-Key: sk_live_admin" http://localhost:5001/admin/metrics
```

### Response Example
```json
{
  "total_api_calls": 1000,
  "total_likes_sent": 5000,
  "avg_response_time": 0.45,
  "error_rate": 0.02,
  "health_status": "healthy"
}
```

## 🔄 Token Refresh Strategy

### Automatic
- Runs every 2 hours (configurable)
- Detects expired tokens automatically
- Visit tokens refreshed first (visit-first strategy)

### Manual
```bash
# Refresh all tokens
curl -H "X-API-Key: sk_live_admin" http://localhost:5001/refresh_tokens

# Refresh visit tokens first
curl -H "X-API-Key: sk_live_admin" http://localhost:5001/refresh_visit_tokens
```

## 📲 Integration with Postman

Import the included Postman collection:
```bash
# Import postman_collection.json in Postman app
```

Or use curl for quick testing (see API_REFERENCE.md)

## 🐛 Troubleshooting

### Database Locked
```bash
pkill -f "python.*app.py"
```

### Reset Everything
```bash
rm -f logs/app.log tokens.db
python -c "from database import TokenDatabase; TokenDatabase().init_db()"
```

### View Errors
```bash
tail -f logs/app.log
```

See [SETUP.md](SETUP.md) for more troubleshooting.

## 📝 Environment Variables

See `.env.example` for complete list. Critical variables:

- `API_HOST` / `API_PORT` - Server address
- `API_KEYS` / `ADMIN_API_KEY` - Authentication
- `ENCRYPTION_KEY` / `ENCRYPTION_IV` - Token encryption
- `DB_SQLITE_PATH` - Database location
- `LOG_LEVEL` / `LOG_FILE` - Logging
- `SCHEDULER_REFRESH_HOURS` - Token refresh interval

## 🤝 Contributing

1. Create feature branch: `git checkout -b feature/improvement`
2. Make changes and test: `python test_modules.py`
3. Commit: `git commit -am "Add improvement"`
4. Push: `git push origin feature/improvement`
5. Create Pull Request

## 📄 License

MIT License - See details in repository

## 🎓 Learn More

- See [SETUP.md](SETUP.md) for detailed setup
- See [API_REFERENCE.md](API_REFERENCE.md) for all endpoints
- See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for deployment
- See [PROJECT_RESEARCH_REPORT.md](PROJECT_RESEARCH_REPORT.md) for architecture

## 🆘 Support

For issues:
1. Check [SETUP.md](SETUP.md) troubleshooting section
2. Review [logs/app.log](logs/app.log) for errors
3. Check GitHub Issues
4. Review [API_REFERENCE.md](API_REFERENCE.md) for endpoint details

## ✨ What's New (Latest Release)

✅ Comprehensive logging system
✅ Input validation module  
✅ SQLite database persistence
✅ API key authentication system
✅ Performance metrics tracking
✅ Rate limiting configuration
✅ Admin monitoring endpoints
✅ GitHub Actions CI/CD
✅ Postman collection
✅ Complete documentation

---

**Status:** Production Ready ✅  
**Version:** 2.0  
**Last Updated:** February 14, 2024
3. 🔄 Generates fresh tokens
4. 💾 Saves to `generated_tokens.json`

## 📦 Output Format

```json
[
  {"token": "eyJhbGciOiJIUzI1NiIsInN2ciI6IjEiLCJ0eXAiOiJKV1QifQ..."},
  {"token": "eyJhbGciOiJIUzI1NiIsInN2ciI6IjEiLCJ0eXAiOiJKV1QifQ..."}
]
```

## 🔧 Requirements

- Python 3.7+
- requests
- aiohttp  
- pycryptodome
- protobuf

## 💡 Alternative Methods

**Windows:** Double-click `RUN_ME.bat`

**Linux/Mac:** `./RUN_ME.sh`

**Single token:** `python token_gen.py <uid> <password>`

---

**That's it!** Simple and clean. 🎉
