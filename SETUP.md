# Setup Instructions

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- SQLite3 (usually included with Python)
- Git (for version control)

## Step-by-Step Setup

### Step 1: Clone Repository
```bash
git clone https://github.com/jahidulislamjihadadv-afk/like.git
cd like
```

### Step 2: Create Virtual Environment (Recommended)
```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Setup Environment Variables
```bash
# Copy example configuration
cp .env.example .env

# Edit .env with your settings
nano .env  # or use your favorite editor
```

### Step 5: Configure Required Settings

Edit `.env` and set these REQUIRED values:

#### API Configuration
```
API_HOST=0.0.0.0
API_PORT=5001
SECRET_KEY=your-secret-key-here
```

#### Security Configuration
```
API_KEYS=sk_live_default
ADDITIONAL_API_KEYS=sk_live_admin
ADMIN_API_KEY=sk_live_admin
ENCRYPTION_KEY=Yg&tc%DEuh6%Zc^8
ENCRYPTION_IV=6oyZDr22E3ychjM%
```

#### Database Configuration
```
DB_TYPE=sqlite
DB_SQLITE_PATH=tokens.db
DB_PERSISTENCE_ENABLED=True
```

#### Logging Configuration
```
LOG_LEVEL=INFO
LOG_FILE=app.log
LOG_MAX_BYTES=10000000
LOG_BACKUP_COUNT=10
```

### Step 6: Initialize Database
```bash
python -c "from database import TokenDatabase; TokenDatabase().init_db()"
```

You should see:
```
✓ Database initialized
Four tables created: tokens, api_logs, token_stats, metrics
```

### Step 7: Test Module Setup
```bash
python test_modules.py
```

Expected output:
```
============================================================
QUICK MODULE TEST SUITE
============================================================
Testing config.py...
  ✓ API Config loaded: 0.0.0.0:5001
  ✓ Security Config loaded: 5 settings
  ✓ Rate Limiting Config loaded: 4 rules
  ✓ Database Config loaded: sqlite
  ✓ Logging Config loaded: level=INFO
  ✓ Token Config loaded: batch_size=189

Testing logger.py...
  ✓ Logger initialized
  ✓ Log file should be at: logs/app.log

Testing validation.py...
  ✓ Valid UID accepted: 1234567890
  ✓ Invalid UID rejected: 123 (too short)
  ✓ Valid server accepted: BD
  ✓ Invalid server rejected: XX
  ✓ Valid API key accepted: sk_live_admin

Testing database.py...
  ✓ Database initialized
  ✓ Token added successfully
  ✓ Retrieved 0 valid tokens
  ✓ API call logged
  ✓ Metrics retrieved: 1 records
  ✓ Token stats retrieved: expected output

Testing auth.py...
  ✓ Generated API key: sk_live_xyz123abc
  ✓ Default API key validation: True
  ✓ Invalid API key detection: True

Testing metrics.py...
  ✓ API call recorded
  ✓ Like sent recorded: BD - 5 likes
  ✓ Health check: healthy
  ✓ Metrics summary retrieved
    - Total API calls: 1
    - Total likes sent: 5
    - Health: healthy

============================================================
TEST SUMMARY
============================================================
  config              ✓ PASS
  logger              ✓ PASS
  validation          ✓ PASS
  database            ✓ PASS
  auth                ✓ PASS
  metrics             ✓ PASS

  Total: 6/6 tests passed

🎉 All modules working correctly!
```

### Step 8: Start Application
```bash
# Development mode (with auto-reload)
python -m flask --app app run --host=0.0.0.0 --port=5001 --debug

# Production mode
python -m app
```

### Step 9: Test API Endpoints
```bash
# In another terminal
# Test health check (public endpoint)
curl http://localhost:5001/token_health

# Test with API key
curl -H "X-API-Key: sk_live_admin" http://localhost:5001/admin/metrics
```

---

## Directory Structure After Setup

```
like/
├── app.py                           # Main Flask application
├── config.py                        # Configuration management
├── logger.py                        # Logging system
├── validation.py                    # Input validation
├── database.py                      # Database layer
├── auth.py                          # Authentication
├── metrics.py                       # Metrics tracking
├── requirements.txt                 # Python dependencies
├── .env.example                     # Environment template
├── .env                             # Environment configuration (created)
├── .gitignore                       # Git ignore rules
├── test_modules.py                  # Module test script
│
├── token_generator/
│   ├── token_gen.py                 # Token generation engine
│   ├── requirements.txt
│   └── ... other files
│
├── templates/
│   └── index.html                   # Web UI
│
├── logs/                            # Log files (created)
│   └── app.log                      # Application log
│
├── tokens.db                        # SQLite database (created)
│
├── README.md                        # Project documentation
├── DEPLOYMENT_GUIDE.md              # Deployment instructions
├── IMPLEMENTATION_CHECKLIST.md      # Integration checklist
└── PROJECT_RESEARCH_REPORT.md       # Research documentation
```

---

## Troubleshooting Setup Issues

### Issue: "ModuleNotFoundError: No module named 'config'"
**Solution:** Make sure you're in the project root directory and all Python files are in the root folder.
```bash
pwd  # Should show: .../workspaces/like
ls config.py logger.py validation.py  # Should all exist
```

### Issue: "ImportError: cannot import name '...' from '...'"
**Solution:** Check that all required dependencies are installed.
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Issue: "DatabaseError: database is locked"
**Solution:** Make sure only one instance of the application is running.
```bash
# Kill any existing instances
pkill -f "python.*app.py"
```

### Issue: ".env file not found"
**Solution:** Create .env file from .env.example
```bash
cp .env.example .env
# Then edit .env with your values
```

### Issue: "No module named 'flask_limiter'"
**Solution:** Install Flask-Limiter
```bash
pip install Flask-Limiter
pip freeze > requirements.txt
```

---

## Next Steps After Setup

1. **Review Configuration:** Check `.env` file has all required values
2. **Check Logs:** Monitor `logs/app.log` for any startup issues
3. **Test Endpoints:** Use curl or Postman to test API endpoints
4. **Integrate into app.py:** Follow `IMPLEMENTATION_CHECKLIST.md`
5. **Run Tests:** Create and run test suite
6. **Deploy:** Follow `DEPLOYMENT_GUIDE.md`

---

## Common Commands

### Start Application
```bash
python -m app
```

### Check Logs
```bash
tail -f logs/app.log
```

### Test API
```bash
# Health check
curl http://localhost:5001/token_health

# Get metrics (requires admin key)
curl -H "X-API-Key: sk_live_admin" http://localhost:5001/admin/metrics

# Send like request (requires API key)
curl -H "X-API-Key: sk_live_admin" "http://localhost:5001/like?uid=1234567890&server=BD"
```

### Database Operations
```bash
# View database tables
sqlite3 tokens.db ".tables"

# Check token count
sqlite3 tokens.db "SELECT COUNT(*) FROM tokens;"

# View recent API logs
sqlite3 tokens.db "SELECT * FROM api_logs ORDER BY timestamp DESC LIMIT 5;"
```

### Reset Everything (Clean Start)
```bash
# Remove logs and database
rm -f logs/app.log tokens.db

# Reinitialize
python -c "from database import TokenDatabase; TokenDatabase().init_db()"

# Clear Python cache
find . -type d -name __pycache__ -exec rm -rf {} +
find . -type f -name "*.pyc" -delete
```

---

## Environment Variables Reference

| Variable | Required | Example | Description |
|----------|----------|---------|-------------|
| API_HOST | Yes | 0.0.0.0 | Server host address |
| API_PORT | Yes | 5001 | Server port number |
| SECRET_KEY | Yes | your-key | Flask secret key |
| API_KEYS | Yes | sk_live_default | Default API key |
| ADMIN_API_KEY | Yes | sk_live_admin | Admin API key |
| ENCRYPTION_KEY | Yes | Yg&tc%DEuh6%Zc^8 | Encryption key (32 chars) |
| ENCRYPTION_IV | Yes | 6oyZDr22E3ychjM% | Encryption IV (16 chars) |
| DB_TYPE | Yes | sqlite | Database type (sqlite/mysql) |
| DB_SQLITE_PATH | Yes | tokens.db | SQLite database path |
| LOG_LEVEL | Yes | INFO | Logging level |
| LOG_FILE | Yes | app.log | Log file name |

---

## Getting Help

If you encounter issues:

1. Check `logs/app.log` for error messages
2. Review `DEPLOYMENT_GUIDE.md` for detailed guidance
3. Check `IMPLEMENTATION_CHECKLIST.md` for integration requirements
4. Read `PROJECT_RESEARCH_REPORT.md` for architecture overview

---

## Installation Verification Checklist

- [ ] Python 3.8+ installed: `python --version`
- [ ] Virtual environment activated: Check prompt shows `(venv)`
- [ ] Dependencies installed: `pip list | grep Flask`
- [ ] .env file created: `ls .env`
- [ ] Database initialized: `sqlite3 tokens.db ".tables"`
- [ ] Module tests passing: `python test_modules.py`
- [ ] Application starting: `python -m app`
- [ ] API responding: `curl http://localhost:5001/token_health`

Once all checks pass, you're ready to integrate modules into app.py!

---

**Setup Status:** Ready for application testing
**Next Phase:** Module Integration (see IMPLEMENTATION_CHECKLIST.md)
