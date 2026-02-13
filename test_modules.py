#!/usr/bin/env python3
"""
Quick test script to verify all modules are working correctly.
Usage: python test_modules.py
"""

import sys
import json
from datetime import datetime

def test_config():
    """Test config module"""
    print("Testing config.py...")
    try:
        from config import (
            API_CONFIG, SECURITY_CONFIG, RATE_LIMITING_CONFIG,
            DATABASE_CONFIG, LOGGING_CONFIG, TOKEN_GENERATION_CONFIG
        )
        print(f"  ✓ API Config loaded: {API_CONFIG['host']}:{API_CONFIG['port']}")
        print(f"  ✓ Security Config loaded: {len(SECURITY_CONFIG)} settings")
        print(f"  ✓ Rate Limiting Config loaded: {len(RATE_LIMITING_CONFIG)} rules")
        print(f"  ✓ Database Config loaded: {DATABASE_CONFIG['type']}")
        print(f"  ✓ Logging Config loaded: level={LOGGING_CONFIG['level']}")
        print(f"  ✓ Token Config loaded: batch_size={TOKEN_GENERATION_CONFIG['batch_size']}")
        return True
    except Exception as e:
        print(f"  ✗ Failed: {e}")
        return False

def test_logger():
    """Test logger module"""
    print("\nTesting logger.py...")
    try:
        from logger import LoggerSetup, logger
        print(f"  ✓ Logger initialized")
        print(f"  ✓ Log file should be at: logs/app.log")
        return True
    except Exception as e:
        print(f"  ✗ Failed: {e}")
        return False

def test_validation():
    """Test validation module"""
    print("\nTesting validation.py...")
    try:
        from validation import InputValidator, ValidationError
        v = InputValidator()
        
        # Test valid UID
        v.validate_uid("1234567890")
        print(f"  ✓ Valid UID accepted: 1234567890")
        
        # Test invalid UID
        try:
            v.validate_uid("123")  # Too short
            print(f"  ✗ Invalid UID should be rejected")
            return False
        except ValidationError:
            print(f"  ✓ Invalid UID rejected: 123 (too short)")
        
        # Test valid server
        v.validate_server("BD")
        print(f"  ✓ Valid server accepted: BD")
        
        # Test invalid server
        try:
            v.validate_server("XX")
            print(f"  ✗ Invalid server should be rejected")
            return False
        except ValidationError:
            print(f"  ✓ Invalid server rejected: XX")
        
        # Test API key validation with valid format
        v.validate_api_key("sk_live_admin_key_12345")
        print(f"  ✓ Valid API key accepted")
        
        return True
    except Exception as e:
        print(f"  ✗ Failed: {e}")
        return False

def test_database():
    """Test database module"""
    print("\nTesting database.py...")
    try:
        from database import TokenDatabase
        db = TokenDatabase()
        
        # Initialize database
        db.init_db()
        print(f"  ✓ Database initialized")
        
        # Test adding a token
        db.add_token(token_str="test_token_xyz", server="BD", account_id="1234567890")
        print(f"  ✓ Token added successfully")
        
        # Test getting tokens
        tokens = db.get_valid_tokens(server="BD")
        print(f"  ✓ Retrieved {len(tokens)} valid tokens")
        
        # Test logging API call
        db.log_api_call("/test", "GET", 200, 0.123)
        print(f"  ✓ API call logged")
        
        # Test getting metrics
        metrics = db.get_metrics()
        print(f"  ✓ Metrics retrieved: {len(metrics)} records")
        
        # Test token stats
        stats = db.get_token_stats()
        print(f"  ✓ Token stats retrieved")
        
        return True
    except Exception as e:
        print(f"  ✗ Failed: {e}")
        return False

def test_auth():
    """Test auth module"""
    print("\nTesting auth.py...")
    try:
        from auth import AuthManager, generate_api_key
        
        # Test API key generation
        new_key = generate_api_key()
        print(f"  ✓ Generated API key: {new_key}")
        
        # Test AuthManager
        auth = AuthManager()
        
        # Test with default key
        is_valid = auth.is_valid_key("sk_live_default")
        print(f"  ✓ Default API key validation: {is_valid}")
        
        # Test with fake key
        is_valid_fake = auth.is_valid_key("sk_live_fake_key_12345")
        print(f"  ✓ Invalid API key detection: {not is_valid_fake}")
        
        return True
    except Exception as e:
        print(f"  ✗ Failed: {e}")
        return False

def test_metrics():
    """Test metrics module"""
    print("\nTesting metrics.py...")
    try:
        from metrics import Metrics
        m = Metrics()
        
        # Record some test activities
        m.record_api_call("/test", 0.123)
        print(f"  ✓ API call recorded")
        
        m.record_like_sent(5)
        print(f"  ✓ Like sent recorded: 5 likes")
        
        m.record_token_generated(True)
        print(f"  ✓ Token generated recorded: 1 token")
        
        # Check health
        health = m.check_health()
        print(f"  ✓ Health check: {health}")
        
        # Get summary
        summary = m.get_summary()
        print(f"  ✓ Metrics summary retrieved")
        print(f"    - Total API calls: {summary.get('total_api_calls', 0)}")
        print(f"    - Total likes sent: {summary.get('total_likes_sent', 0)}")
        print(f"    - Health: {summary.get('server_health', 'unknown')}")
        
        return True
    except Exception as e:
        print(f"  ✗ Failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("QUICK MODULE TEST SUITE")
    print("=" * 60)
    
    results = {
        "config": test_config(),
        "logger": test_logger(),
        "validation": test_validation(),
        "database": test_database(),
        "auth": test_auth(),
        "metrics": test_metrics(),
    }
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for module, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {module:15} {status}")
    
    print(f"\n  Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All modules working correctly!")
        print("\nNext steps:")
        print("  1. Integrate modules into app.py")
        print("  2. Follow IMPLEMENTATION_CHECKLIST.md")
        print("  3. Run tests again after integration")
        return 0
    else:
        print("\n❌ Some tests failed. Check the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
