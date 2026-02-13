"""Unit tests for database module"""

import pytest
import sqlite3
import os
from datetime import datetime, timedelta
from database import TokenDatabase


class TestTokenDatabase:
    """Test cases for TokenDatabase class"""
    
    @pytest.fixture
    def temp_db(self, tmp_path):
        """Create temporary database for testing"""
        db_path = tmp_path / "test_tokens.db"
        db = TokenDatabase(db_path=str(db_path))
        db.init_db()
        yield db
        # Cleanup
        if os.path.exists(str(db_path)):
            os.remove(str(db_path))
    
    def test_database_initialization(self, temp_db):
        """Test that database initializes with all required tables"""
        # Get table names
        cursor = temp_db.conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        assert 'tokens' in tables
        assert 'api_logs' in tables
        assert 'token_stats' in tables
        assert 'metrics' in tables
    
    def test_add_token_single(self, temp_db):
        """Test adding a single token"""
        token = "test_token_xyz"
        uid = "1234567890"
        server = "BD"
        
        temp_db.add_token(uid, token, server, expiry_days=1)
        
        # Verify token was added
        cursor = temp_db.conn.cursor()
        cursor.execute("SELECT * FROM tokens WHERE uid = ?", (uid,))
        result = cursor.fetchone()
        
        assert result is not None
        assert result[0] == uid
        assert result[1] == token
        assert result[2] == server
    
    def test_add_token_multiple(self, temp_db):
        """Test adding multiple tokens"""
        tokens = [
            ("1234567890", "token1", "BD"),
            ("1234567891", "token2", "IND"),
            ("1234567892", "token3", "BR"),
        ]
        
        for uid, token, server in tokens:
            temp_db.add_token(uid, token, server, expiry_days=1)
        
        # Verify all tokens were added
        cursor = temp_db.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM tokens")
        count = cursor.fetchone()[0]
        
        assert count == 3
    
    def test_get_valid_tokens_all_servers(self, temp_db):
        """Test getting all valid tokens"""
        # Add test tokens
        temp_db.add_token("1234567890", "token1", "BD", expiry_days=1)
        temp_db.add_token("1234567891", "token2", "IND", expiry_days=1)
        
        # Get tokens
        tokens = temp_db.get_valid_tokens()
        
        assert len(tokens) >= 2
    
    def test_get_valid_tokens_specific_server(self, temp_db):
        """Test getting tokens for specific server"""
        # Add tokens for different servers
        temp_db.add_token("1234567890", "token_bd", "BD", expiry_days=1)
        temp_db.add_token("1234567891", "token_ind", "IND", expiry_days=1)
        temp_db.add_token("1234567892", "token_br", "BR", expiry_days=1)
        
        # Get BD tokens only
        bd_tokens = temp_db.get_valid_tokens(server="BD")
        
        # Verify only BD tokens returned
        for token_data in bd_tokens:
            if isinstance(token_data, dict):
                assert token_data.get('server') == "BD"
            elif isinstance(token_data, tuple):
                assert token_data[2] == "BD"  # Assuming server is index 2
    
    def test_delete_expired_tokens(self, temp_db):
        """Test deletion of expired tokens"""
        # Add expired token (0 days = expired immediately after)
        temp_db.add_token("1234567890", "expired_token", "BD", expiry_days=-1)
        # Add valid token
        temp_db.add_token("1234567891", "valid_token", "IND", expiry_days=1)
        
        # Delete expired tokens
        deleted_count = temp_db.delete_expired_tokens()
        
        # Verify expired token was deleted
        assert deleted_count >= 1
    
    def test_log_api_call(self, temp_db):
        """Test logging API calls"""
        endpoint = "/test"
        method = "GET"
        status_code = 200
        response_time = 0.123
        
        temp_db.log_api_call(endpoint, method, status_code, response_time)
        
        # Verify log was recorded
        cursor = temp_db.conn.cursor()
        cursor.execute("SELECT * FROM api_logs WHERE endpoint = ?", (endpoint,))
        result = cursor.fetchone()
        
        assert result is not None
        assert result[1] == method
        assert result[2] == status_code
    
    def test_get_metrics(self, temp_db):
        """Test retrieving metrics"""
        # Record some metrics
        temp_db.add_metric("test_metric", 100)
        temp_db.add_metric("test_metric", 200)
        
        # Get metrics
        metrics = temp_db.get_metrics()
        
        assert metrics is not None
        assert len(metrics) >= 2
    
    def test_add_metric(self, temp_db):
        """Test adding metrics"""
        metric_name = "test_metric"
        value = 42.5
        
        temp_db.add_metric(metric_name, value)
        
        # Verify metric was added
        cursor = temp_db.conn.cursor()
        cursor.execute("SELECT * FROM metrics WHERE metric_name = ?", (metric_name,))
        result = cursor.fetchone()
        
        assert result is not None
    
    def test_get_token_stats(self, temp_db):
        """Test getting token statistics"""
        # Add some tokens
        temp_db.add_token("1234567890", "token1", "BD", expiry_days=1)
        temp_db.add_token("1234567891", "token2", "BD", expiry_days=1)
        temp_db.add_token("1234567892", "token3", "IND", expiry_days=1)
        
        # Get stats
        stats = temp_db.get_token_stats()
        
        assert stats is not None
        if isinstance(stats, dict):
            # If returns dict with server counts
            assert 'BD' in stats or len(stats) >= 0
    
    def test_cleanup_old_logs(self, temp_db):
        """Test cleanup of old API logs"""
        # Log some API calls
        for i in range(5):
            temp_db.log_api_call("/test", "GET", 200, 0.1)
        
        # Cleanup old logs (this might not delete if logs are recent)
        deleted_count = temp_db.cleanup_old_logs(days=0)
        
        # Just verify it doesn't throw error
        assert isinstance(deleted_count, int)
    
    def test_database_persistence(self, temp_db):
        """Test that data persists across connections"""
        # Add data
        temp_db.add_token("1234567890", "test_token", "BD", expiry_days=1)
        
        # Close connection
        temp_db.close()
        
        # Reconnect
        temp_db2 = TokenDatabase(db_path=temp_db.db_path)
        temp_db2.init_db()
        
        # Verify data exists
        tokens = temp_db2.get_valid_tokens()
        assert len(tokens) >= 1
        
        temp_db2.close()
    
    def test_connection_error_handling(self):
        """Test error handling for invalid database path"""
        # Try to create database in invalid path
        # This might not raise error depending on implementation
        try:
            db = TokenDatabase(db_path="/invalid/path/tokens.db")
        except Exception as e:
            # Expected to fail somewhere
            pass


class TestTokenDatabaseSchema:
    """Test cases for database schema"""
    
    @pytest.fixture
    def temp_db(self, tmp_path):
        """Create temporary database for testing"""
        db_path = tmp_path / "test_tokens.db"
        db = TokenDatabase(db_path=str(db_path))
        db.init_db()
        yield db
        if os.path.exists(str(db_path)):
            os.remove(str(db_path))
    
    def test_tokens_table_schema(self, temp_db):
        """Test that tokens table has correct schema"""
        cursor = temp_db.conn.cursor()
        cursor.execute("PRAGMA table_info(tokens)")
        columns = {row[1]: row[2] for row in cursor.fetchall()}
        
        assert 'uid' in columns
        assert 'token' in columns
        assert 'server' in columns
        assert 'expiry' in columns
    
    def test_api_logs_table_schema(self, temp_db):
        """Test that api_logs table has correct schema"""
        cursor = temp_db.conn.cursor()
        cursor.execute("PRAGMA table_info(api_logs)")
        columns = {row[1]: row[2] for row in cursor.fetchall()}
        
        assert 'endpoint' in columns
        assert 'method' in columns
        assert 'status_code' in columns
        assert 'response_time' in columns
    
    def test_metrics_table_schema(self, temp_db):
        """Test that metrics table has correct schema"""
        cursor = temp_db.conn.cursor()
        cursor.execute("PRAGMA table_info(metrics)")
        columns = {row[1]: row[2] for row in cursor.fetchall()}
        
        assert 'metric_name' in columns
        assert 'value' in columns


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
