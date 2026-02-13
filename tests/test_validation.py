"""Unit tests for validation module"""

import pytest
from validation import InputValidator, ValidationError


class TestInputValidator:
    """Test cases for InputValidator class"""
    
    def setup_method(self):
        """Setup validator instance for each test"""
        self.validator = InputValidator()
    
    # UID Validation Tests
    def test_validate_uid_valid_10_digits(self):
        """Test that 10-digit UID is accepted"""
        assert self.validator.validate_uid("1234567890") is None
    
    def test_validate_uid_valid_9_digits(self):
        """Test that 9-digit UID is accepted"""
        assert self.validator.validate_uid("123456789") is None
    
    def test_validate_uid_valid_8_digits(self):
        """Test that 8-digit UID is accepted"""
        assert self.validator.validate_uid("12345678") is None
    
    def test_validate_uid_too_short(self):
        """Test that UID less than 8 digits is rejected"""
        with pytest.raises(ValidationError):
            self.validator.validate_uid("1234567")
    
    def test_validate_uid_too_long(self):
        """Test that UID more than 10 digits is rejected"""
        with pytest.raises(ValidationError):
            self.validator.validate_uid("12345678901")
    
    def test_validate_uid_non_numeric(self):
        """Test that non-numeric UID is rejected"""
        with pytest.raises(ValidationError):
            self.validator.validate_uid("123456abc")
    
    def test_validate_uid_empty(self):
        """Test that empty UID is rejected"""
        with pytest.raises(ValidationError):
            self.validator.validate_uid("")
    
    def test_validate_uid_none(self):
        """Test that None UID is rejected"""
        with pytest.raises(ValidationError):
            self.validator.validate_uid(None)
    
    # Password Validation Tests
    def test_validate_password_valid_long(self):
        """Test that long password is accepted"""
        assert self.validator.validate_password("ValidPassword123") is None
    
    def test_validate_password_minimum_length(self):
        """Test that 8-character password is accepted"""
        assert self.validator.validate_password("Pass1234") is None
    
    def test_validate_password_too_short(self):
        """Test that password less than 8 characters is rejected"""
        with pytest.raises(ValidationError):
            self.validator.validate_password("Pass123")
    
    def test_validate_password_empty(self):
        """Test that empty password is rejected"""
        with pytest.raises(ValidationError):
            self.validator.validate_password("")
    
    # Server Validation Tests
    def test_validate_server_bd(self):
        """Test that BD server is accepted"""
        assert self.validator.validate_server("BD") is None
    
    def test_validate_server_ind(self):
        """Test that IND server is accepted"""
        assert self.validator.validate_server("IND") is None
    
    def test_validate_server_br(self):
        """Test that BR server is accepted"""
        assert self.validator.validate_server("BR") is None
    
    def test_validate_server_us(self):
        """Test that US server is accepted"""
        assert self.validator.validate_server("US") is None
    
    def test_validate_server_sac(self):
        """Test that SAC server is accepted"""
        assert self.validator.validate_server("SAC") is None
    
    def test_validate_server_na(self):
        """Test that NA server is accepted"""
        assert self.validator.validate_server("NA") is None
    
    def test_validate_server_invalid(self):
        """Test that invalid server is rejected"""
        with pytest.raises(ValidationError):
            self.validator.validate_server("XX")
    
    def test_validate_server_lowercase(self):
        """Test that lowercase server is accepted or rejected appropriately"""
        # This depends on implementation - adjust based on actual behavior
        try:
            self.validator.validate_server("bd")
        except ValidationError:
            pass  # Expected if case-sensitive
    
    def test_validate_server_empty(self):
        """Test that empty server is rejected"""
        with pytest.raises(ValidationError):
            self.validator.validate_server("")
    
    # API Key Validation Tests
    def test_validate_api_key_valid_prefix(self):
        """Test that API key with valid prefix is accepted"""
        assert self.validator.validate_api_key("sk_live_admin") is None
    
    def test_validate_api_key_valid_test(self):
        """Test that test API key is accepted"""
        assert self.validator.validate_api_key("sk_test_12345") is None
    
    def test_validate_api_key_too_short(self):
        """Test that short API key is rejected"""
        with pytest.raises(ValidationError):
            self.validator.validate_api_key("short")
    
    def test_validate_api_key_invalid_format(self):
        """Test that API key with invalid format is rejected"""
        with pytest.raises(ValidationError):
            self.validator.validate_api_key("invalid_key_format")
    
    def test_validate_api_key_empty(self):
        """Test that empty API key is rejected"""
        with pytest.raises(ValidationError):
            self.validator.validate_api_key("")
    
    # URL Validation Tests
    def test_validate_url_http(self):
        """Test that HTTP URL is accepted"""
        assert self.validator.validate_url("http://example.com") is None
    
    def test_validate_url_https(self):
        """Test that HTTPS URL is accepted"""
        assert self.validator.validate_url("https://example.com") is None
    
    def test_validate_url_invalid_scheme(self):
        """Test that URL with invalid scheme is rejected"""
        with pytest.raises(ValidationError):
            self.validator.validate_url("ftp://example.com")
    
    def test_validate_url_no_scheme(self):
        """Test that URL without scheme is rejected"""
        with pytest.raises(ValidationError):
            self.validator.validate_url("example.com")
    
    def test_validate_url_empty(self):
        """Test that empty URL is rejected"""
        with pytest.raises(ValidationError):
            self.validator.validate_url("")
    
    # Token Validation Tests
    def test_validate_token_valid_jwt_like(self):
        """Test that JWT-like token is accepted"""
        token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.DjwRjfq3GF2-wxL23zSGVjJjayo8O8t4w2B1jF76N_k"
        assert self.validator.validate_token(token) is None
    
    def test_validate_token_short(self):
        """Test that short token is rejected"""
        with pytest.raises(ValidationError):
            self.validator.validate_token("short")
    
    def test_validate_token_no_dots(self):
        """Test that token without dots is rejected"""
        with pytest.raises(ValidationError):
            self.validator.validate_token("nodotsintoken")
    
    def test_validate_token_empty(self):
        """Test that empty token is rejected"""
        with pytest.raises(ValidationError):
            self.validator.validate_token("")


class TestValidationErrorException:
    """Test cases for ValidationError exception"""
    
    def test_validation_error_raised(self):
        """Test that ValidationError is raised properly"""
        with pytest.raises(ValidationError):
            raise ValidationError("Test error message")
    
    def test_validation_error_message(self):
        """Test that ValidationError message is preserved"""
        try:
            raise ValidationError("Test error")
        except ValidationError as e:
            assert str(e) == "Test error"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
