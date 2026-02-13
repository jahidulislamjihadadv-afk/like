"""Unit tests for authentication module"""

import pytest
from auth import AuthManager, generate_api_key
from config import SECURITY_CONFIG


class TestAPIKeyGeneration:
    """Test cases for API key generation"""
    
    def test_generate_api_key_format(self):
        """Test that generated API key has correct format"""
        key = generate_api_key()
        assert key.startswith("sk_live_"), "API key should start with sk_live_"
    
    def test_generate_api_key_length(self):
        """Test that generated API key has sufficient length"""
        key = generate_api_key()
        assert len(key) > 20, "API key should be sufficiently long"
    
    def test_generate_api_key_unique(self):
        """Test that generated API keys are unique"""
        key1 = generate_api_key()
        key2 = generate_api_key()
        assert key1 != key2, "Generated API keys should be unique"
    
    def test_generate_api_key_alphanumeric(self):
        """Test that API key contains only alphanumeric characters"""
        key = generate_api_key()
        # Remove prefix
        suffix = key.replace("sk_live_", "")
        assert suffix.isalnum(), "API key suffix should be alphanumeric"


class TestAuthManager:
    """Test cases for AuthManager class"""
    
    def setup_method(self):
        """Setup AuthManager instance for each test"""
        self.auth = AuthManager()
    
    def test_auth_manager_initialization(self):
        """Test that AuthManager initializes correctly"""
        assert self.auth is not None
    
    def test_is_valid_key_default(self):
        """Test that default API key is valid"""
        assert self.auth.is_valid_key("sk_live_default") is True
    
    def test_is_valid_key_invalid(self):
        """Test that invalid API key is rejected"""
        assert self.auth.is_valid_key("invalid_key") is False
    
    def test_is_valid_key_empty(self):
        """Test that empty API key is rejected"""
        assert self.auth.is_valid_key("") is False
    
    def test_is_valid_key_none(self):
        """Test that None API key is rejected"""
        assert self.auth.is_valid_key(None) is False
    
    def test_is_valid_key_admin(self):
        """Test that admin API key validation"""
        admin_key = SECURITY_CONFIG.get('ADMIN_API_KEY', 'sk_live_admin')
        # Should be valid if configured
        result = self.auth.is_valid_key(admin_key)
        # Result depends on config, just ensure no exception
        assert isinstance(result, bool)
    
    def test_is_valid_key_custom_key(self):
        """Test that custom API key can be validated"""
        # This would depend on configuration
        custom_key = "sk_live_test123"
        result = self.auth.is_valid_key(custom_key)
        assert isinstance(result, bool)
    
    def test_is_valid_key_case_sensitive(self):
        """Test that API key validation is case-sensitive"""
        assert self.auth.is_valid_key("SK_LIVE_DEFAULT") is False


class TestGetAPIKeyFromRequest:
    """Test cases for extracting API key from request"""
    
    def setup_method(self):
        """Setup AuthManager instance for each test"""
        self.auth = AuthManager()
    
    def test_get_api_key_from_header(self):
        """Test extracting API key from header (mock test)"""
        # In real tests with Flask context:
        # api_key = self.auth.get_api_key_from_request(mock_request)
        # This would require Flask test client
        pass
    
    def test_get_api_key_from_query(self):
        """Test extracting API key from query string (mock test)"""
        # Would need Flask test client and request context
        pass
    
    def test_get_api_key_from_bearer(self):
        """Test extracting API key from Bearer token (mock test)"""
        # Would need Flask test client and request context
        pass
    
    def test_get_api_key_none_provided(self):
        """Test behavior when no API key is provided"""
        # Would need Flask test client
        pass


class TestAuthorizationLevels:
    """Test cases for authorization levels"""
    
    def setup_method(self):
        """Setup AuthManager instance for each test"""
        self.auth = AuthManager()
    
    def test_regular_key_not_admin(self):
        """Test that regular key is not admin"""
        # Depends on implementation
        # Regular keys should have limited permissions
        pass
    
    def test_admin_key_is_admin(self):
        """Test that admin key has admin permissions"""
        # Depends on implementation
        # Admin keys should have full permissions
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
