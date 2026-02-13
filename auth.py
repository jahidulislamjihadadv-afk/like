"""
API Authentication Module
Secure API access with API keys and authorization
"""

from functools import wraps
from flask import request, jsonify
from config import SECURITY_CONFIG
from logger import log_security_event
import os

class AuthManager:
    """Manage API authentication"""
    
    def __init__(self):
        self.api_keys = set(SECURITY_CONFIG['api_keys'])
        # Load additional keys from environment
        env_keys = os.getenv('ADDITIONAL_API_KEYS', '')
        if env_keys:
            self.api_keys.update(env_keys.split(','))
    
    def is_valid_key(self, api_key):
        """Check if API key is valid"""
        if not api_key:
            return False
        
        is_valid = api_key.strip() in self.api_keys
        
        if not is_valid:
            log_security_event("INVALID_API_KEY", f"Attempted with: {api_key[:10]}...")
        
        return is_valid
    
    def get_api_key_from_request(self, req):
        """Extract API key from request"""
        # Try header first
        api_key = req.headers.get('X-API-Key')
        
        # Try query parameter as backup
        if not api_key:
            api_key = req.args.get('api_key')
        
        # Try authorization bearer
        if not api_key:
            auth = req.headers.get('Authorization')
            if auth and auth.startswith('Bearer '):
                api_key = auth[7:]
        
        return api_key
    
    def add_api_key(self, api_key):
        """Add new API key"""
        if api_key not in self.api_keys:
            self.api_keys.add(api_key)
            log_security_event("API_KEY_ADDED", f"New key: {api_key[:10]}...")
            return True
        return False
    
    def revoke_api_key(self, api_key):
        """Revoke an API key"""
        if api_key in self.api_keys:
            self.api_keys.remove(api_key)
            log_security_event("API_KEY_REVOKED", f"Key: {api_key[:10]}...")
            return True
        return False

# Initialize auth manager
auth_manager = AuthManager()

# =================== Decorators ===================

def require_api_key(f):
    """Decorator to require API key"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = auth_manager.get_api_key_from_request(request)
        
        if not api_key:
            log_security_event("MISSING_API_KEY", f"Endpoint: {request.path}")
            return jsonify({"error": "API key required"}), 401
        
        if not auth_manager.is_valid_key(api_key):
            log_security_event("UNAUTHORIZED_API_KEY", f"Endpoint: {request.path}")
            return jsonify({"error": "Invalid API key"}), 401
        
        return f(*args, **kwargs)
    return decorated_function

def optional_api_key(f):
    """Decorator for optional API key (public endpoints)"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = auth_manager.get_api_key_from_request(request)
        
        if api_key and not auth_manager.is_valid_key(api_key):
            log_security_event("INVALID_API_KEY_PROVIDED", f"Endpoint: {request.path}")
            return jsonify({"error": "Invalid API key"}), 401
        
        return f(*args, **kwargs)
    return decorated_function

def require_admin_key(f):
    """Decorator for admin endpoints"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = auth_manager.get_api_key_from_request(request)
        admin_key = os.getenv('ADMIN_API_KEY')
        
        if not admin_key:
            return jsonify({"error": "Admin key not configured"}), 500
        
        if api_key != admin_key:
            log_security_event("ADMIN_ACCESS_DENIED", f"Endpoint: {request.path}")
            return jsonify({"error": "Admin access required"}), 403
        
        return f(*args, **kwargs)
    return decorated_function

# =================== Utility Functions ===================

def generate_api_key(prefix="sk_live_"):
    """Generate a new API key"""
    import secrets
    random_part = secrets.token_urlsafe(32)
    return f"{prefix}{random_part}"

def hash_sensitive_string(s):
    """Hash sensitive string for logging"""
    return s[:10] + "****" + s[-4:] if len(s) > 14 else "****"
