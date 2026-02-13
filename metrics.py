"""
Metrics and Monitoring Module
Tracks performance metrics and application health
"""

import json
from datetime import datetime
from logger import logger
from database import db

class Metrics:
    """Track application metrics"""
    
    def __init__(self):
        self.stats = {
            "total_likes_sent": 0,
            "total_tokens_generated": 0,
            "failed_token_generations": 0,
            "total_api_calls": 0,
            "total_api_errors": 0,
            "total_tokens_deleted": 0,
            "average_response_time": 0,
            "last_refresh_time": None,
            "uptime_seconds": 0,
            "server_health": "healthy"
        }
        self.response_times = []
    
    def record_like_sent(self, likes_count):
        """Record successful like sent"""
        self.stats["total_likes_sent"] += likes_count
        db.add_metric("likes_sent", likes_count)
    
    def record_token_generated(self, success=True):
        """Record token generation"""
        if success:
            self.stats["total_tokens_generated"] += 1
            db.add_metric("tokens_generated", 1)
        else:
            self.stats["failed_token_generations"] += 1
            db.add_metric("token_generation_failed", 1)
    
    def record_api_call(self, endpoint, response_time, success=True, error=None):
        """Record API call"""
        self.stats["total_api_calls"] += 1
        if not success:
            self.stats["total_api_errors"] += 1
        
        # Track response time
        self.response_times.append(response_time)
        if len(self.response_times) > 1000:  # Keep only last 1000
            self.response_times.pop(0)
        
        # Update average
        if self.response_times:
            self.stats["average_response_time"] = sum(self.response_times) / len(self.response_times)
        
        # Log to database
        status_code = 200 if success else 500
        db.log_api_call(endpoint, "GET/POST", status_code, response_time, error)
    
    def record_token_cleanup(self, count):
        """Record token cleanup"""
        self.stats["total_tokens_deleted"] += count
        db.add_metric("tokens_cleaned", count)
    
    def record_refresh(self):
        """Record token refresh"""
        self.stats["last_refresh_time"] = datetime.now().isoformat()
        db.add_metric("token_refresh", 1)
    
    def get_error_rate(self):
        """Calculate error rate"""
        if self.stats["total_api_calls"] == 0:
            return 0
        return (self.stats["total_api_errors"] / self.stats["total_api_calls"]) * 100
    
    def check_health(self):
        """Check server health"""
        error_rate = self.get_error_rate()
        
        if error_rate < 1:
            self.stats["server_health"] = "healthy"
        elif error_rate < 5:
            self.stats["server_health"] = "degraded"
        else:
            self.stats["server_health"] = "unhealthy"
        
        return self.stats["server_health"]
    
    def get_summary(self):
        """Get metrics summary"""
        return {
            "timestamp": datetime.now().isoformat(),
            "health": self.check_health(),
            "stats": self.stats,
            "error_rate": f"{self.get_error_rate():.2f}%",
            "response_times": {
                "min": min(self.response_times) if self.response_times else 0,
                "max": max(self.response_times) if self.response_times else 0,
                "avg": self.stats["average_response_time"]
            }
        }
    
    def reset(self):
        """Reset metrics"""
        self.stats = {
            "total_likes_sent": 0,
            "total_tokens_generated": 0,
            "failed_token_generations": 0,
            "total_api_calls": 0,
            "total_api_errors": 0,
            "total_tokens_deleted": 0,
            "average_response_time": 0,
            "last_refresh_time": None,
            "uptime_seconds": 0,
            "server_health": "healthy"
        }
        self.response_times = []
        logger.info("📊 Metrics reset")

# Initialize metrics
metrics = Metrics()

# Functions for easy access
def track_api_call(endpoint, response_time, success=True, error=None):
    """Track API call (wrapper function)"""
    metrics.record_api_call(endpoint, response_time, success, error)

def track_like_sent(count):
    """Track like sent"""
    metrics.record_like_sent(count)

def track_token_generated(success=True):
    """Track token generation"""
    metrics.record_token_generated(success)

def get_metrics_summary():
    """Get metrics summary"""
    return metrics.get_summary()
