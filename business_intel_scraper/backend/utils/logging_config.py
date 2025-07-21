"""
Enhanced Logging Configuration for Visual Analytics Platform
Provides structured logging with performance monitoring and security audit trails
"""

import logging
import logging.handlers
import json
import os
import sys
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from pathlib import Path
import traceback
from contextvars import ContextVar
from dataclasses import dataclass, asdict

# Context variables for request tracking
request_id_var: ContextVar[Optional[str]] = ContextVar('request_id', default=None)
user_id_var: ContextVar[Optional[str]] = ContextVar('user_id', default=None)
session_id_var: ContextVar[Optional[str]] = ContextVar('session_id', default=None)

@dataclass
class LogContext:
    """Structured context for log entries"""
    timestamp: str
    level: str
    message: str
    module: str
    function: str
    line_number: int
    request_id: Optional[str] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    duration_ms: Optional[float] = None
    memory_mb: Optional[float] = None
    extra_data: Optional[Dict[str, Any]] = None

class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging"""
    
    def format(self, record: logging.LogRecord) -> str:
        # Get context information
        request_id = request_id_var.get()
        user_id = user_id_var.get()
        session_id = session_id_var.get()
        
        # Extract memory usage if available
        memory_mb = None
        if hasattr(record, 'memory_mb'):
            memory_mb = record.memory_mb
            
        # Extract duration if available
        duration_ms = None
        if hasattr(record, 'duration_ms'):
            duration_ms = record.duration_ms
        
        # Create log context
        log_context = LogContext(
            timestamp=datetime.now(timezone.utc).isoformat(),
            level=record.levelname,
            message=record.getMessage(),
            module=record.module,
            function=record.funcName,
            line_number=record.lineno,
            request_id=request_id,
            user_id=user_id,
            session_id=session_id,
            duration_ms=duration_ms,
            memory_mb=memory_mb,
            extra_data=getattr(record, 'extra_data', None)
        )
        
        # Convert to dict and remove None values
        log_dict = {k: v for k, v in asdict(log_context).items() if v is not None}
        
        # Add exception information if present
        if record.exc_info:
            log_dict['exception'] = {
                'type': record.exc_info[0].__name__,
                'message': str(record.exc_info[1]),
                'traceback': traceback.format_exception(*record.exc_info)
            }
        
        return json.dumps(log_dict, default=str)

class PerformanceLogger:
    """Logger specifically for performance metrics"""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.start_time: Optional[float] = None
    
    def start_timer(self):
        """Start performance timing"""
        import time
        self.start_time = time.perf_counter()
    
    def log_performance(self, operation: str, **kwargs):
        """Log performance metrics"""
        import time
        import psutil
        
        if self.start_time:
            duration_ms = (time.perf_counter() - self.start_time) * 1000
        else:
            duration_ms = None
            
        # Get memory usage
        process = psutil.Process()
        memory_mb = process.memory_info().rss / 1024 / 1024
        
        extra_data = {
            'operation': operation,
            'cpu_percent': process.cpu_percent(),
            **kwargs
        }
        
        self.logger.info(
            f"Performance: {operation}",
            extra={
                'duration_ms': duration_ms,
                'memory_mb': memory_mb,
                'extra_data': extra_data
            }
        )

class SecurityLogger:
    """Logger specifically for security events"""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
    
    def log_authentication(self, user_id: str, success: bool, ip_address: str, user_agent: str):
        """Log authentication attempts"""
        self.logger.info(
            f"Authentication {'successful' if success else 'failed'} for user {user_id}",
            extra={
                'extra_data': {
                    'event_type': 'authentication',
                    'user_id': user_id,
                    'success': success,
                    'ip_address': ip_address,
                    'user_agent': user_agent
                }
            }
        )
    
    def log_authorization(self, user_id: str, resource: str, action: str, granted: bool):
        """Log authorization attempts"""
        self.logger.info(
            f"Authorization {'granted' if granted else 'denied'} for user {user_id} on {resource}",
            extra={
                'extra_data': {
                    'event_type': 'authorization',
                    'user_id': user_id,
                    'resource': resource,
                    'action': action,
                    'granted': granted
                }
            }
        )
    
    def log_data_access(self, user_id: str, data_type: str, record_count: int):
        """Log data access events"""
        self.logger.info(
            f"Data access: user {user_id} accessed {record_count} {data_type} records",
            extra={
                'extra_data': {
                    'event_type': 'data_access',
                    'user_id': user_id,
                    'data_type': data_type,
                    'record_count': record_count
                }
            }
        )

def setup_logging(
    log_level: str = "INFO",
    log_file: str = "/app/logs/application.log",
    max_size: str = "100MB",
    backup_count: int = 5,
    json_format: bool = True
) -> Dict[str, logging.Logger]:
    """
    Set up comprehensive logging configuration
    Returns dict of specialized loggers
    """
    
    # Create logs directory if it doesn't exist
    log_dir = Path(log_file).parent
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Parse max_size
    if max_size.endswith('MB'):
        max_bytes = int(max_size[:-2]) * 1024 * 1024
    elif max_size.endswith('GB'):
        max_bytes = int(max_size[:-2]) * 1024 * 1024 * 1024
    else:
        max_bytes = int(max_size)
    
    # Choose formatter
    if json_format:
        formatter = JSONFormatter()
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
    
    # File handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=max_bytes,
        backupCount=backup_count
    )
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)
    
    # Console handler for development
    if os.getenv('APP_ENV', 'development') == 'development':
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
    
    # Create specialized loggers
    loggers = {
        'app': logging.getLogger('visual_analytics.app'),
        'api': logging.getLogger('visual_analytics.api'),
        'database': logging.getLogger('visual_analytics.database'),
        'websocket': logging.getLogger('visual_analytics.websocket'),
        'performance': logging.getLogger('visual_analytics.performance'),
        'security': logging.getLogger('visual_analytics.security'),
        'audit': logging.getLogger('visual_analytics.audit'),
    }
    
    # Set up performance logger
    perf_file = log_file.replace('.log', '_performance.log')
    perf_handler = logging.handlers.RotatingFileHandler(
        perf_file,
        maxBytes=max_bytes,
        backupCount=backup_count
    )
    perf_handler.setFormatter(formatter)
    loggers['performance'].addHandler(perf_handler)
    loggers['performance'].setLevel(logging.INFO)
    
    # Set up security/audit logger
    security_file = log_file.replace('.log', '_security.log')
    security_handler = logging.handlers.RotatingFileHandler(
        security_file,
        maxBytes=max_bytes,
        backupCount=backup_count
    )
    security_handler.setFormatter(formatter)
    loggers['security'].addHandler(security_handler)
    loggers['audit'].addHandler(security_handler)
    loggers['security'].setLevel(logging.INFO)
    loggers['audit'].setLevel(logging.INFO)
    
    return loggers

# Context managers for request tracking
class RequestContext:
    """Context manager for tracking requests"""
    
    def __init__(self, request_id: str, user_id: Optional[str] = None, session_id: Optional[str] = None):
        self.request_id = request_id
        self.user_id = user_id
        self.session_id = session_id
        self.tokens = []
    
    def __enter__(self):
        self.tokens.append(request_id_var.set(self.request_id))
        if self.user_id:
            self.tokens.append(user_id_var.set(self.user_id))
        if self.session_id:
            self.tokens.append(session_id_var.set(self.session_id))
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        for token in reversed(self.tokens):
            token.var.reset(token)

# Global logger instances
LOGGERS = setup_logging(
    log_level=os.getenv('LOG_LEVEL', 'INFO'),
    log_file=os.getenv('LOG_FILE', '/app/logs/application.log'),
    max_size=os.getenv('LOG_MAX_SIZE', '100MB'),
    backup_count=int(os.getenv('LOG_BACKUP_COUNT', '5')),
    json_format=os.getenv('LOG_FORMAT', 'json') == 'json'
)

# Convenience functions
def get_logger(name: str = 'app') -> logging.Logger:
    """Get a logger by name"""
    return LOGGERS.get(name, LOGGERS['app'])

def get_performance_logger() -> PerformanceLogger:
    """Get performance logger instance"""
    return PerformanceLogger(LOGGERS['performance'])

def get_security_logger() -> SecurityLogger:
    """Get security logger instance"""
    return SecurityLogger(LOGGERS['security'])

# Example usage
if __name__ == "__main__":
    # Test the logging configuration
    app_logger = get_logger('app')
    perf_logger = get_performance_logger()
    security_logger = get_security_logger()
    
    with RequestContext('req-123', user_id='user-456', session_id='sess-789'):
        app_logger.info("Application started successfully")
        
        perf_logger.start_timer()
        # Simulate some work
        import time
        time.sleep(0.1)
        perf_logger.log_performance("startup_time", component="main")
        
        security_logger.log_authentication('user-456', True, '192.168.1.1', 'Mozilla/5.0')
        security_logger.log_data_access('user-456', 'entities', 150)
        
        app_logger.error("Test error with context", extra={'extra_data': {'test': 'value'}})
