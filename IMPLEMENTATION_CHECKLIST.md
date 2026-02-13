# Implementation Checklist for app.py Integration

## Phase 1: Module Integration (Priority: CRITICAL)

### 1. Import New Modules
- [ ] Add `from config import *` at top of app.py
- [ ] Add `from logger import LoggerSetup, log_api_request, log_error_with_context`
- [ ] Add `from validation import InputValidator, ValidationError`
- [ ] Add `from database import TokenDatabase`
- [ ] Add `from auth import AuthManager, require_api_key, optional_api_key, require_admin_key`
- [ ] Add `from metrics import Metrics`

### 2. Initialize Module Instances
- [ ] Create `logger = LoggerSetup.setup()` after imports
- [ ] Create `validator = InputValidator()` after imports
- [ ] Create `db = TokenDatabase()` after imports
- [ ] Call `db.init_db()` to initialize database
- [ ] Create `auth_manager = AuthManager()` after imports
- [ ] Create `metrics = Metrics()` after imports
- [ ] Replace hardcoded ENCRYPTION_KEY with `SECURITY_CONFIG['ENCRYPTION_KEY']`
- [ ] Replace hardcoded ENCRYPTION_IV with `SECURITY_CONFIG['ENCRYPTION_IV']`

### 3. Configure Flask-Limiter
- [ ] Install Flask-Limiter: `pip install Flask-Limiter`
- [ ] Import `from flask_limiter import Limiter`
- [ ] Import `from flask_limiter.util import get_remote_address`
- [ ] Create limiter: `limiter = Limiter(app=app, key_func=get_remote_address)`
- [ ] Add rate limiting decorators to endpoints (see Phase 2)

---

## Phase 2: Endpoint Security & Validation

### 1. Protected Endpoints (Require API Key)
- [ ] `/like` - Add `@require_api_key`
- [ ] `/refresh_tokens` - Add `@require_api_key`
- [ ] `/refresh_visit_tokens` - Add `@require_api_key`
- [ ] `/token_health` - Add `@optional_api_key` (allow public access, log API calls if key provided)
- [ ] `/admin/metrics` - Add `@require_admin_key`
- [ ] `/admin/cleanup` - Add `@require_admin_key`
- [ ] `/admin/health` - Add `@require_admin_key`

### 2. Add Input Validation
- [ ] In `/like` endpoint:
  - [ ] Validate UID: `validator.validate_uid(uid)`
  - [ ] Validate server: `validator.validate_server(server)`
  - [ ] Validate token: `validator.validate_token(token)` if provided
  - [ ] Return 400 for validation errors

### 3. Add Rate Limiting
- [ ] `/like` - Add `@limiter.limit(RATE_LIMITING_CONFIG['RATE_LIKE_LIMIT'])`
- [ ] `/refresh_tokens` - Add `@limiter.limit(RATE_LIMITING_CONFIG['RATE_REFRESH_LIMIT'])`
- [ ] `/token_health` - Add `@limiter.limit(RATE_LIMITING_CONFIG['RATE_HEALTH_LIMIT'])`
- [ ] All other endpoints - Add `@limiter.limit(RATE_LIMITING_CONFIG['RATE_DEFAULT_LIMIT'])`

---

## Phase 3: Error Handling & Logging

### 1. Wrap Endpoints in Try-Except
```python
@app.route('/like', methods=['GET', 'POST'])
@require_api_key
@limiter.limit("20 per hour")
def like():
    try:
        # endpoint logic
        return jsonify(result), 200
    except ValidationError as e:
        log_error_with_context('ValidationError in /like', str(e), request)
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        log_error_with_context('Exception in /like', str(e), request)
        return jsonify({'error': 'Internal server error'}), 500
```

### 2. Add Request/Response Logging
- [ ] For each endpoint, add: `log_api_request(request, endpoint_name)`
- [ ] For successful responses, add: `logger.info(f"{endpoint_name}: {status_code}")`
- [ ] For errors, add: `log_error_with_context(endpoint_name, error_message, request)`

### 3. Track Metrics
- [ ] In `like()` endpoint: `metrics.record_like_sent(server, len(successful_uids))`
- [ ] In `refresh_tokens()`: `metrics.record_token_generated(len(new_tokens))`
- [ ] In token cleanup: `metrics.record_token_cleanup(deleted_count)`
- [ ] For all API calls: `metrics.record_api_call(endpoint, response_time)`

---

## Phase 4: Database Integration

### 1. Replace Token Loading
- [ ] In `load_tokens()` function:
  - [ ] Replace: `with open(f'token_{server}.json', 'r') as f:`
  - [ ] With: `tokens_list = db.get_valid_tokens(server=server)`
  - [ ] If empty, trigger refresh: `refresh_tokens_now(server)`

### 2. Add Token Storage
- [ ] In token generation loop, add: `db.add_token(uid, token, server, expiry_days=1)`
- [ ] In token refresh, add: `db.add_token(uid, new_token, server, expiry_days=1)`
- [ ] Before using tokens, add: `db.delete_expired_tokens()`

### 3. API Call Logging
- [ ] For each endpoint, add: `db.log_api_call(endpoint, method, status_code, response_time)`
- [ ] At end of endpoint handler, calculate response_time and log

### 4. Token Cleanup Integration
- [ ] In scheduler, add: `deleted = db.delete_expired_tokens()`
- [ ] Log: `logger.info(f"Cleanup: deleted {deleted} expired tokens")`
- [ ] Add to `/admin/cleanup` endpoint: `deleted = db.delete_expired_tokens()`

---

## Phase 5: New Endpoints

### 1. Add Admin Endpoints
- [ ] Create `/admin/metrics` - Returns metrics summary
  - [ ] Protected with `@require_admin_key`
  - [ ] Returns: `metrics.get_summary()`
  
- [ ] Create `/admin/health` - Returns database statistics
  - [ ] Protected with `@require_admin_key`
  - [ ] Returns: Token count, expiry info, API stats
  
- [ ] Create `/admin/cleanup` - Manually trigger token cleanup
  - [ ] Protected with `@require_admin_key`
  - [ ] Calls: `db.delete_expired_tokens()`
  - [ ] Returns: Count of deleted tokens

### 2. Public Status Endpoints
- [ ] Update `/token_health` - Use database instead of file reading
  - [ ] Make it `@optional_api_key` (public but logs API calls)
  - [ ] Use `db.get_token_stats()` for statistics

---

## Phase 6: Configuration Management

### 1. Use Config for All Settings
- [ ] Replace hardcoded values:
  - [ ] `API_HOST` → `API_CONFIG['API_HOST']`
  - [ ] `API_PORT` → `API_CONFIG['API_PORT']`
  - [ ] DEBUG → `API_CONFIG['DEBUG']`
  - [ ] Encryption keys → `SECURITY_CONFIG['ENCRYPTION_KEY']`
  - [ ] Rate limits → `RATE_LIMITING_CONFIG`
  - [ ] Token expiry → `TOKEN_GENERATION_CONFIG['TOKEN_EXPIRY_DAYS']`
  - [ ] Scheduler interval → `SCHEDULER_CONFIG['REFRESH_HOURS']`

### 2. Load from .env file
- [ ] Ensure `from dotenv import load_dotenv` at top of app.py
- [ ] Call `load_dotenv()` before using config

---

## Phase 7: Error Handling & Response Standards

### 1. Standardize API Responses
```python
# Success response
{'status': 'success', 'data': {...}, 'timestamp': datetime}

# Error response
{'status': 'error', 'message': 'error details', 'code': 'ERROR_CODE', 'timestamp': datetime}

# Validation error
{'status': 'error', 'message': 'Validation failed', 'errors': {'field': 'error_message'}}
```

### 2. Add Error Codes
- [ ] `INVALID_UID` - UID format invalid
- [ ] `INVALID_SERVER` - Server not in allowed list
- [ ] `INVALID_TOKEN` - Token format invalid
- [ ] `INVALID_API_KEY` - API key invalid or missing
- [ ] `RATE_LIMIT_EXCEEDED` - Too many requests
- [ ] `NO_VALID_TOKENS` - No valid tokens available
- [ ] `REFRESH_FAILED` - Token refresh failed
- [ ] `INTERNAL_ERROR` - Server error

---

## Phase 8: Testing

### 1. Unit Tests (Create test_app.py)
- [ ] Test validation functions
- [ ] Test authentication decorators
- [ ] Test database operations
- [ ] Test metrics tracking

### 2. Integration Tests
- [ ] Test /like endpoint with valid request
- [ ] Test /like endpoint with invalid UID
- [ ] Test /like endpoint without API key
- [ ] Test /refresh_tokens endpoint
- [ ] Test /admin/metrics with admin key
- [ ] Test /admin/metrics without admin key (should fail)

### 3. Load Tests
- [ ] Test rate limiting (send 25 requests to /like, expect 4xx after 20)
- [ ] Test concurrent requests
- [ ] Test token cleanup performance

---

## Phase 9: Documentation

### 1. Update README.md
- [ ] Add configuration section
- [ ] Add API endpoint documentation
- [ ] Add authentication section
- [ ] Add rate limiting documentation

### 2. Update Deployment Guide
- [ ] Add module initialization steps
- [ ] Add environment setup instructions
- [ ] Add troubleshooting section

### 3. Add Inline Code Comments
- [ ] Document all new authentication requirements
- [ ] Document all database operations
- [ ] Document all metrics tracking points

---

## Phase 10: Deployment & Monitoring

### 1. Pre-deployment Checklist
- [ ] All tests passing
- [ ] All env variables documented
- [ ] Database initialized
- [ ] API keys configured
- [ ] Rate limits configured
- [ ] Logging configured
- [ ] No hardcoded secrets in code

### 2. Deploy
- [ ] Create `.env` from `.env.example`
- [ ] Configure production values
- [ ] Run database migrations if needed
- [ ] Deploy to Vercel / Docker / Server
- [ ] Verify all endpoints working
- [ ] Monitor logs for errors

### 3. Post-deployment Monitoring
- [ ] Monitor `/admin/metrics` regularly
- [ ] Check error rate in logs
- [ ] Verify token refresh running on schedule
- [ ] Monitor database size (tokens.db)
- [ ] Set up alerts for critical errors

---

## Implementation Order

1. **First:** Phase 1 (Module Integration) - Get all imports working
2. **Second:** Phase 2 & 3 (Security & Logging) - Protect endpoints
3. **Third:** Phase 4 (Database Integration) - Replace file-based storage
4. **Fourth:** Phase 6 (Config Management) - Replace hardcoded values
5. **Fifth:** Phase 5 (New Endpoints) - Add admin endpoints
6. **Sixth:** Phase 8 (Testing) - Write test suite
7. **Finally:** Phase 9 & 10 (Documentation & Deployment)

---

## Quick Commands

### Initialize Everything
```bash
cp .env.example .env
pip install -r requirements.txt
python -c "from database import TokenDatabase; TokenDatabase().init_db()"
python -m app
```

### Test API
```bash
# Get metrics (requires admin key)
curl -H "X-API-Key: sk_live_admin" http://localhost:5001/admin/metrics

# Send like (requires API key)
curl -H "X-API-Key: sk_live_admin" "http://localhost:5001/like?uid=1234567890&server=BD"

# Check health (public)
curl http://localhost:5001/token_health
```

### Monitor
```bash
# Watch logs
tail -f logs/app.log

# Check metrics
python -c "from metrics import Metrics; print(Metrics().get_summary())"

# Check database
sqlite3 tokens.db ".tables"
sqlite3 tokens.db "SELECT COUNT(*) FROM tokens;"
```

---

## Success Criteria

After completing all phases:
- ✅ All endpoints protected and authenticated
- ✅ All inputs validated
- ✅ All requests logged
- ✅ All API calls tracked in metrics
- ✅ All tokens stored in database
- ✅ All tests passing
- ✅ Comprehensive documentation
- ✅ Production-ready deployment

---

**Status:** Ready for Phase 1 implementation
**Estimated Time:** 2-3 hours for full integration
**Next Step:** Start with Phase 1 - Module Integration
