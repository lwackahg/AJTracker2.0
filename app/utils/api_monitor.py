"""
API Monitor: Tracks and analyzes API performance metrics.
"""
from datetime import datetime, timedelta
from collections import deque
from threading import Lock
from typing import Dict, Any, Deque
from functools import wraps
from flask import request, current_app
import time

class APIMonitor:
    """Singleton class for monitoring API performance metrics."""
    
    _instance = None
    _lock = Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(APIMonitor, cls).__new__(cls)
                    cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize monitoring data structures."""
        self._response_times: Deque[float] = deque(maxlen=1000)  # Last 1000 response times
        self._requests: Deque[datetime] = deque(maxlen=1000)     # Last 1000 request timestamps
        self._errors: Deque[datetime] = deque(maxlen=1000)       # Last 1000 error timestamps
    
    @classmethod
    def track_request(cls, func):
        """Decorator to track API request metrics."""
        @wraps(func)
        def wrapper(*args, **kwargs):
            instance = cls()
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                end_time = time.time()
                
                # Record response time
                instance._response_times.append(end_time - start_time)
                
                # Record request timestamp
                instance._requests.append(datetime.utcnow())
                
                return result
                
            except Exception as e:
                # Record error
                instance._errors.append(datetime.utcnow())
                current_app.logger.error(f"API Error in {func.__name__}: {str(e)}")
                raise
                
        return wrapper
    
    @classmethod
    def get_average_response_time(cls) -> float:
        """Get average response time over the last 1000 requests."""
        instance = cls()
        if not instance._response_times:
            return 0.0
        return sum(instance._response_times) / len(instance._response_times)
    
    @classmethod
    def get_requests_per_minute(cls) -> float:
        """Calculate requests per minute based on recent requests."""
        instance = cls()
        if not instance._requests:
            return 0.0
            
        now = datetime.utcnow()
        minute_ago = now - timedelta(minutes=1)
        
        # Count requests in the last minute
        recent_requests = sum(1 for req_time in instance._requests 
                            if req_time >= minute_ago)
        
        return recent_requests
    
    @classmethod
    def get_error_rate(cls) -> float:
        """Calculate error rate as percentage of total requests."""
        instance = cls()
        if not instance._requests:
            return 0.0
            
        now = datetime.utcnow()
        hour_ago = now - timedelta(hours=1)
        
        # Count errors and requests in the last hour
        recent_errors = sum(1 for err_time in instance._errors 
                          if err_time >= hour_ago)
        recent_requests = sum(1 for req_time in instance._requests 
                            if req_time >= hour_ago)
        
        if recent_requests == 0:
            return 0.0
            
        return (recent_errors / recent_requests) * 100
    
    @classmethod
    def get_all_metrics(cls) -> Dict[str, Any]:
        """Get all API metrics in a single call."""
        return {
            'average_response_time': cls.get_average_response_time(),
            'requests_per_minute': cls.get_requests_per_minute(),
            'error_rate': cls.get_error_rate(),
            'timestamp': datetime.utcnow()
        }
