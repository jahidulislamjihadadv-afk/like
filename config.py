"""
Configuration and Environment Variables
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# =================== API Configuration ===================
API_CONFIG = {
    "host": os.getenv("API_HOST", "0.0.0.0"),
    "port": int(os.getenv("API_PORT", 5001)),
    "debug": os.getenv("DEBUG", "False").lower() == "true",
    "secret_key": os.getenv("SECRET_KEY", "your-secret-key-change-in-production"),
}

# =================== Security Configuration ===================
SECURITY_CONFIG = {
    "api_keys": os.getenv("API_KEYS", "sk_live_default").split(","),
    "encryption_key": os.getenv("ENCRYPTION_KEY", "Yg&tc%DEuh6%Zc^8"),
    "encryption_iv": os.getenv("ENCRYPTION_IV", "6oyZDr22E3ychjM%"),
    "enable_ssl_verification": os.getenv("ENABLE_SSL_VERIFICATION", "False").lower() == "true",
}

# =================== Rate Limiting Configuration ===================
RATE_LIMITING_CONFIG = {
    "enabled": os.getenv("RATE_LIMITING_ENABLED", "True").lower() == "true",
    "like_endpoint": os.getenv("RATE_LIKE_LIMIT", "20 per hour"),
    "refresh_endpoint": os.getenv("RATE_REFRESH_LIMIT", "5 per day"),
    "token_health": os.getenv("RATE_HEALTH_LIMIT", "100 per hour"),
    "default": os.getenv("RATE_DEFAULT_LIMIT", "200 per day"),
}

# =================== Database Configuration ===================
DATABASE_CONFIG = {
    "type": os.getenv("DB_TYPE", "sqlite"),
    "sqlite_path": os.getenv("DB_SQLITE_PATH", "tokens.db"),
    "mysql_url": os.getenv("DB_MYSQL_URL", "mysql://user:pass@localhost/like"),
    "enable_persistence": os.getenv("DB_PERSISTENCE_ENABLED", "True").lower() == "true",
}

# =================== Logging Configuration ===================
LOGGING_CONFIG = {
    "level": os.getenv("LOG_LEVEL", "INFO"),
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": os.getenv("LOG_FILE", "app.log"),
    "max_bytes": int(os.getenv("LOG_MAX_BYTES", 10000000)),
    "backup_count": int(os.getenv("LOG_BACKUP_COUNT", 10)),
}

# =================== Token Generator Configuration ===================
TOKEN_GENERATION_CONFIG = {
    "batch_size": int(os.getenv("TOKEN_BATCH_SIZE", 189)),
    "timeout": int(os.getenv("TOKEN_TIMEOUT", 15)),
    "max_retries": int(os.getenv("TOKEN_MAX_RETRIES", 3)),
    "parallel_workers": int(os.getenv("TOKEN_PARALLEL_WORKERS", 2)),
    "delay_between_requests": int(os.getenv("TOKEN_DELAY", 2)),
}

# =================== Notification Configuration ===================
NOTIFICATION_CONFIG = {
    "enabled": os.getenv("NOTIFICATIONS_ENABLED", "False").lower() == "true",
    "email": os.getenv("NOTIFY_EMAIL", ""),
    "email_password": os.getenv("NOTIFY_EMAIL_PASSWORD", ""),
    "webhook_url": os.getenv("WEBHOOK_URL", ""),
}

# =================== Scheduler Configuration ===================
SCHEDULER_CONFIG = {
    "enabled": os.getenv("SCHEDULER_ENABLED", "True").lower() == "true",
    "refresh_hours": int(os.getenv("SCHEDULER_REFRESH_HOURS", 2)),
    "refresh_before_expiry_days": int(os.getenv("SCHEDULER_REFRESH_BEFORE_DAYS", 1)),
}

# =================== Performance Configuration ===================
PERFORMANCE_CONFIG = {
    "enable_caching": os.getenv("CACHING_ENABLED", "True").lower() == "true",
    "cache_ttl": int(os.getenv("CACHE_TTL", 300)),
    "connection_pool_size": int(os.getenv("POOL_SIZE", 100)),
}

# =================== Monitor Configuration ===================
MONITOR_CONFIG = {
    "enabled": os.getenv("MONITORING_ENABLED", "True").lower() == "true",
    "metrics_file": os.getenv("METRICS_FILE", "metrics.json"),
}
