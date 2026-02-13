"""
Database Module for Token Persistence
Stores tokens in database for better management and persistence
"""

import sqlite3
import json
from datetime import datetime
from logger import logger
from config import DATABASE_CONFIG

class TokenDatabase:
    """SQLite database for token storage"""
    
    def __init__(self, db_path=None):
        self.db_path = db_path or DATABASE_CONFIG['sqlite_path']
        self.init_db()
    
    def init_db(self):
        """Initialize database with required tables"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            # Tokens table
            c.execute('''CREATE TABLE IF NOT EXISTS tokens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                token TEXT NOT NULL UNIQUE,
                server TEXT NOT NULL,
                account_id TEXT,
                nickname TEXT,
                generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                status TEXT DEFAULT 'active',
                is_valid BOOLEAN DEFAULT 1
            )''')
            
            # API Logs table
            c.execute('''CREATE TABLE IF NOT EXISTS api_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                endpoint TEXT,
                method TEXT,
                status_code INTEGER,
                response_time REAL,
                error TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''')
            
            # Token Stats table
            c.execute('''CREATE TABLE IF NOT EXISTS token_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                server TEXT,
                total_tokens INTEGER,
                valid_tokens INTEGER,
                expired_tokens INTEGER,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''')
            
            # Metrics table
            c.execute('''CREATE TABLE IF NOT EXISTS metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_name TEXT,
                metric_value REAL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''')
            
            conn.commit()
            conn.close()
            logger.info("✅ Database initialized successfully")
        except Exception as e:
            logger.error(f"❌ Database init error: {e}")
    
    def add_token(self, token_str, server, account_id=None, nickname=None, expires_at=None):
        """Add token to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            c.execute('''INSERT INTO tokens 
                        (token, server, account_id, nickname, expires_at, status, is_valid)
                        VALUES (?, ?, ?, ?, ?, ?, ?)''',
                     (token_str, server, account_id, nickname, expires_at, 'active', 1))
            
            conn.commit()
            conn.close()
            logger.info(f"✅ Token added: {server} - {nickname}")
            return True
        except sqlite3.IntegrityError:
            logger.warning(f"⚠️  Token already exists: {token_str[:20]}...")
            return False
        except Exception as e:
            logger.error(f"❌ Error adding token: {e}")
            return False
    
    def get_valid_tokens(self, server):
        """Get all valid (non-expired) tokens for a server"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            c.execute('''SELECT token, account_id, nickname FROM tokens
                        WHERE server = ? AND is_valid = 1 AND status = 'active'
                        AND (expires_at IS NULL OR expires_at > CURRENT_TIMESTAMP)
                        ORDER BY generated_at DESC''', (server,))
            
            tokens = [{'token': row[0], 'account_id': row[1], 'nickname': row[2]} 
                     for row in c.fetchall()]
            conn.close()
            return tokens
        except Exception as e:
            logger.error(f"❌ Error getting tokens: {e}")
            return []
    
    def delete_expired_tokens(self):
        """Delete all expired tokens"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            c.execute('''UPDATE tokens SET is_valid = 0, status = 'expired'
                        WHERE expires_at < CURRENT_TIMESTAMP AND is_valid = 1''')
            
            deleted = c.rowcount
            conn.commit()
            conn.close()
            
            logger.info(f"🧹 Deleted {deleted} expired tokens")
            return deleted
        except Exception as e:
            logger.error(f"❌ Error deleting expired tokens: {e}")
            return 0
    
    def log_api_call(self, endpoint, method, status_code, response_time, error=None):
        """Log API request"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            c.execute('''INSERT INTO api_logs 
                        (endpoint, method, status_code, response_time, error)
                        VALUES (?, ?, ?, ?, ?)''',
                     (endpoint, method, status_code, response_time, error))
            
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"❌ Error logging API call: {e}")
    
    def get_metrics(self, metric_name=None):
        """Get metrics from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            if metric_name:
                c.execute('SELECT metric_value, timestamp FROM metrics WHERE metric_name = ? ORDER BY timestamp DESC LIMIT 100',
                         (metric_name,))
            else:
                c.execute('SELECT metric_name, metric_value, timestamp FROM metrics ORDER BY timestamp DESC LIMIT 1000')
            
            result = c.fetchall()
            conn.close()
            return result
        except Exception as e:
            logger.error(f"❌ Error getting metrics: {e}")
            return []
    
    def add_metric(self, metric_name, metric_value):
        """Add metric to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            c.execute('''INSERT INTO metrics (metric_name, metric_value)
                        VALUES (?, ?)''', (metric_name, metric_value))
            
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"❌ Error adding metric: {e}")
    
    def get_token_stats(self, server=None):
        """Get token statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            if server:
                c.execute('''SELECT 
                            COUNT(*) as total,
                            SUM(CASE WHEN is_valid = 1 THEN 1 ELSE 0 END) as valid,
                            SUM(CASE WHEN is_valid = 0 THEN 1 ELSE 0 END) as expired
                            FROM tokens WHERE server = ?''', (server,))
            else:
                c.execute('''SELECT 
                            COUNT(*) as total,
                            SUM(CASE WHEN is_valid = 1 THEN 1 ELSE 0 END) as valid,
                            SUM(CASE WHEN is_valid = 0 THEN 1 ELSE 0 END) as expired
                            FROM tokens''')
            
            result = c.fetchone()
            conn.close()
            
            return {
                'total': result[0] or 0,
                'valid': result[1] or 0,
                'expired': result[2] or 0
            }
        except Exception as e:
            logger.error(f"❌ Error getting token stats: {e}")
            return {'total': 0, 'valid': 0, 'expired': 0}
    
    def cleanup_old_logs(self, days=30):
        """Clean old API logs"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            c.execute('''DELETE FROM api_logs 
                        WHERE created_at < datetime('now', '-' || ? || ' days')''', (days,))
            
            deleted = c.rowcount
            conn.commit()
            conn.close()
            
            logger.info(f"🧹 Cleaned {deleted} old log entries")
            return deleted
        except Exception as e:
            logger.error(f"❌ Error cleaning logs: {e}")
            return 0

# Initialize database
db = TokenDatabase()
