"""
Input Validation Module
Validates all user inputs for security and correctness
"""

import re
from logger import log_security_event

class ValidationError(Exception):
    """Custom validation error"""
    pass

class InputValidator:
    """Validate all user inputs"""
    
    # Constants
    VALID_SERVERS = {"BD", "IND", "BR", "US", "SAC", "NA"}
    UID_PATTERN = re.compile(r'^\d{8,10}$')  # 8-10 digits
    PASSWORD_PATTERN = re.compile(r'^[A-Za-z0-9_\-]{5,}$')  # Alphanumeric, min 5
    TOKEN_PATTERN = re.compile(r'^[A-Za-z0-9_\-\.]+$')  # JWT pattern
    
    @staticmethod
    def validate_uid(uid):
        """Validate Free Fire UID format"""
        if not uid:
            raise ValidationError("UID is required")
        
        uid_str = str(uid).strip()
        
        if not InputValidator.UID_PATTERN.match(uid_str):
            log_security_event("INVALID_UID", f"Attempted with: {uid_str}")
            raise ValidationError(f"Invalid UID format. Must be 8-10 digits, got: {uid_str}")
        
        return uid_str
    
    @staticmethod
    def validate_password(password):
        """Validate password format"""
        if not password:
            raise ValidationError("Password is required")
        
        if len(password) < 5:
            raise ValidationError("Password too short (min 5 characters)")
        
        if len(password) > 100:
            raise ValidationError("Password too long (max 100 characters)")
        
        return password
    
    @staticmethod
    def validate_server(server):
        """Validate server name"""
        if not server:
            raise ValidationError("Server name is required")
        
        server_upper = server.upper().strip()
        
        if server_upper not in InputValidator.VALID_SERVERS:
            log_security_event("INVALID_SERVER", f"Attempted with: {server}")
            raise ValidationError(
                f"Invalid server '{server}'. Must be one of: {', '.join(InputValidator.VALID_SERVERS)}"
            )
        
        return server_upper
    
    @staticmethod
    def validate_token(token):
        """Validate JWT token format"""
        if not token:
            raise ValidationError("Token is required")
        
        if not InputValidator.TOKEN_PATTERN.match(token):
            raise ValidationError("Invalid token format")
        
        if len(token) < 100:
            raise ValidationError("Token too short to be valid")
        
        return token
    
    @staticmethod
    def validate_like_count(count):
        """Validate like count"""
        try:
            count_int = int(count)
        except (ValueError, TypeError):
            raise ValidationError("Like count must be a number")
        
        if count_int < 0:
            raise ValidationError("Like count cannot be negative")
        
        if count_int > 1000000:
            raise ValidationError("Like count seems too high")
        
        return count_int
    
    @staticmethod
    def validate_api_key(api_key):
        """Validate API key format"""
        if not api_key:
            raise ValidationError("API key is required")
        
        if not api_key.startswith("sk_"):
            raise ValidationError("Invalid API key format")
        
        if len(api_key) < 20:
            raise ValidationError("API key too short")
        
        return api_key
    
    @staticmethod
    def validate_url(url):
        """Validate URL format"""
        if not url:
            raise ValidationError("URL is required")
        
        if not url.startswith(('http://', 'https://')):
            raise ValidationError("URL must start with http:// or https://")
        
        return url
    
    @staticmethod
    def sanitize_string(string_input):
        """Remove potentially dangerous characters"""
        if not string_input:
            return ""
        
        # Remove special characters except alphanumeric and basic punctuation
        sanitized = re.sub(r'[<>"]', '', str(string_input))
        return sanitized[:255]  # Max 255 chars


# Batch validation
def validate_token_generation_request(uid, password):
    """Validate token generation request"""
    try:
        validated_uid = InputValidator.validate_uid(uid)
        validated_password = InputValidator.validate_password(password)
        return validated_uid, validated_password
    except ValidationError as e:
        log_security_event("INVALID_TOKEN_REQUEST", str(e))
        raise

def validate_like_request(uid, server):
    """Validate like request"""
    try:
        validated_uid = InputValidator.validate_uid(uid)
        validated_server = InputValidator.validate_server(server)
        return validated_uid, validated_server
    except ValidationError as e:
        log_security_event("INVALID_LIKE_REQUEST", str(e))
        raise
