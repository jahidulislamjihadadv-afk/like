"""
Comprehensive Logging System
Logs all API calls, errors, and important events
"""

import logging
import logging.handlers
import os
from config import LOGGING_CONFIG
from datetime import datetime

class LoggerSetup:
    def __init__(self, name="like_bot"):
        self.name = name
        self.logger = self._setup_logger()
    
    def _setup_logger(self):
        """Setup logger with file and console handlers"""
        logger = logging.getLogger(self.name)
        logger.setLevel(LOGGING_CONFIG['level'])
        
        # Create formatter
        formatter = logging.Formatter(LOGGING_CONFIG['format'])
        
        # File handler with rotation
        os.makedirs('logs', exist_ok=True)
        log_file = f"logs/{LOGGING_CONFIG['file']}"
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=LOGGING_CONFIG['max_bytes'],
            backupCount=LOGGING_CONFIG['backup_count']
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        
        # Add handlers
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
    
    def get_logger(self):
        return self.logger

# Initialize main logger
logger = LoggerSetup().get_logger()

# =================== Logging Utilities ===================

def log_api_request(endpoint, method, params):
    """Log API request"""
    logger.info(f"📡 API Request: {method} {endpoint} | Params: {params}")

def log_api_response(endpoint, status_code, response_time):
    """Log API response"""
    logger.info(f"✅ API Response: {endpoint} | Status: {status_code} | Time: {response_time}ms")

def log_api_error(endpoint, error, status_code=500):
    """Log API error"""
    logger.error(f"❌ API Error: {endpoint} | Status: {status_code} | Error: {error}")

def log_token_generated(uid, success, account_name=None):
    """Log token generation"""
    if success:
        logger.info(f"✅ Token Generated: UID={uid} ({account_name})")
    else:
        logger.error(f"❌ Token Generation Failed: UID={uid}")

def log_like_sent(uid, likes_count, server, success):
    """Log like sending"""
    if success:
        logger.info(f"✅ Likes Sent: UID={uid} | Count={likes_count} | Server={server}")
    else:
        logger.error(f"❌ Like Send Failed: UID={uid} | Server={server}")

def log_token_expired(server, token_summary):
    """Log token expiry"""
    logger.warning(f"⚠️  Token Expired: {server} | Summary: {token_summary}")

def log_token_cleanup(server, count):
    """Log token cleanup"""
    logger.info(f"🧹 Tokens Cleaned: {server} | Count: {count}")

def log_scheduler_event(event_name, details):
    """Log scheduler events"""
    logger.info(f"⏰ Scheduler: {event_name} | Details: {details}")

def log_error_with_context(error, context):
    """Log error with full context"""
    logger.error(f"💥 Error: {error} | Context: {context}", exc_info=True)

def log_security_event(event_type, details):
    """Log security events"""
    logger.warning(f"🔐 Security: {event_type} | Details: {details}")
