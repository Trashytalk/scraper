#!/usr/bin/env python3
"""
Enhanced Error Handling and User Feedback System
Comprehensive error management, user notifications, and feedback collection
"""

import traceback
import logging
import json
import time
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
import uuid

class ErrorSeverity(Enum):
    """Error severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ErrorCategory(Enum):
    """Error categories"""
    VALIDATION = "validation"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    NETWORK = "network"
    DATABASE = "database"
    EXTERNAL_API = "external_api"
    SYSTEM = "system"
    USER_INPUT = "user_input"
    BUSINESS_LOGIC = "business_logic"
    PERFORMANCE = "performance"

@dataclass
class ErrorDetails:
    """Detailed error information"""
    error_id: str
    category: ErrorCategory
    severity: ErrorSeverity
    message: str
    user_message: str
    technical_details: Dict[str, Any]
    timestamp: datetime
    request_id: Optional[str] = None
    user_id: Optional[str] = None
    endpoint: Optional[str] = None
    stack_trace: Optional[str] = None
    context: Dict[str, Any] = None
    suggested_actions: List[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'error_id': self.error_id,
            'category': self.category.value,
            'severity': self.severity.value,
            'message': self.message,
            'user_message': self.user_message,
            'technical_details': self.technical_details,
            'timestamp': self.timestamp.isoformat(),
            'request_id': self.request_id,
            'user_id': self.user_id,
            'endpoint': self.endpoint,
            'stack_trace': self.stack_trace,
            'context': self.context or {},
            'suggested_actions': self.suggested_actions or []
        }
    
    def to_user_response(self) -> Dict[str, Any]:
        """Convert to user-friendly response"""
        return {
            'success': False,
            'error': {
                'id': self.error_id,
                'message': self.user_message,
                'category': self.category.value,
                'severity': self.severity.value,
                'suggested_actions': self.suggested_actions or [],
                'timestamp': self.timestamp.isoformat()
            }
        }

class ErrorHandler:
    """Comprehensive error handling system"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = self._setup_logging()
        self.error_history: Dict[str, ErrorDetails] = {}
        self.error_patterns: Dict[str, Dict[str, Any]] = {}
        self._load_error_patterns()
    
    def _setup_logging(self) -> logging.Logger:
        """Setup error logging"""
        logger = logging.getLogger('error_handler')
        logger.setLevel(logging.INFO)
        
        # File handler for errors
        file_handler = logging.FileHandler('logs/errors.log')
        file_formatter = logging.Formatter(
            '%(asctime)s - ERROR - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
        
        return logger
    
    def _load_error_patterns(self):
        """Load common error patterns and their handling"""
        self.error_patterns = {
            'connection_timeout': {
                'category': ErrorCategory.NETWORK,
                'severity': ErrorSeverity.MEDIUM,
                'user_message': 'Connection timeout occurred. Please try again.',
                'suggested_actions': [
                    'Check your internet connection',
                    'Try again in a few moments',
                    'Contact support if the problem persists'
                ]
            },
            'validation_error': {
                'category': ErrorCategory.VALIDATION,
                'severity': ErrorSeverity.LOW,
                'user_message': 'Invalid input provided.',
                'suggested_actions': [
                    'Check the required fields',
                    'Ensure data is in the correct format',
                    'Review the input requirements'
                ]
            },
            'authentication_failed': {
                'category': ErrorCategory.AUTHENTICATION,
                'severity': ErrorSeverity.MEDIUM,
                'user_message': 'Authentication failed. Please check your credentials.',
                'suggested_actions': [
                    'Verify your username and password',
                    'Check if your account is active',
                    'Try logging out and logging back in'
                ]
            },
            'insufficient_permissions': {
                'category': ErrorCategory.AUTHORIZATION,
                'severity': ErrorSeverity.MEDIUM,
                'user_message': 'You do not have permission to perform this action.',
                'suggested_actions': [
                    'Contact your administrator',
                    'Verify your role and permissions',
                    'Try logging out and logging back in'
                ]
            },
            'database_error': {
                'category': ErrorCategory.DATABASE,
                'severity': ErrorSeverity.HIGH,
                'user_message': 'A database error occurred. Our team has been notified.',
                'suggested_actions': [
                    'Try again in a few moments',
                    'Contact support if the problem persists',
                    'Check if there are any ongoing maintenance activities'
                ]
            },
            'rate_limit_exceeded': {
                'category': ErrorCategory.PERFORMANCE,
                'severity': ErrorSeverity.MEDIUM,
                'user_message': 'Rate limit exceeded. Please slow down your requests.',
                'suggested_actions': [
                    'Wait a few minutes before trying again',
                    'Reduce the frequency of your requests',
                    'Consider upgrading your plan for higher limits'
                ]
            },
            'external_api_error': {
                'category': ErrorCategory.EXTERNAL_API,
                'severity': ErrorSeverity.MEDIUM,
                'user_message': 'External service is temporarily unavailable.',
                'suggested_actions': [
                    'Try again in a few minutes',
                    'Check the service status page',
                    'Contact support if the issue persists'
                ]
            },
            'system_overload': {
                'category': ErrorCategory.SYSTEM,
                'severity': ErrorSeverity.HIGH,
                'user_message': 'System is currently overloaded. Please try again later.',
                'suggested_actions': [
                    'Try again in a few minutes',
                    'Use the system during off-peak hours',
                    'Contact support for assistance'
                ]
            }
        }
    
    def identify_error_pattern(self, error: Exception, context: Dict[str, Any]) -> Optional[str]:
        """Identify error pattern from exception and context"""
        error_str = str(error).lower()
        error_type = type(error).__name__.lower()
        
        # Pattern matching logic
        if 'timeout' in error_str or 'connectionerror' in error_type:
            return 'connection_timeout'
        elif 'validation' in error_str or 'invalid' in error_str:
            return 'validation_error'
        elif 'authentication' in error_str or 'login' in error_str:
            return 'authentication_failed'
        elif 'permission' in error_str or 'unauthorized' in error_str:
            return 'insufficient_permissions'
        elif 'database' in error_str or 'sql' in error_str:
            return 'database_error'
        elif 'rate limit' in error_str or 'too many requests' in error_str:
            return 'rate_limit_exceeded'
        elif context.get('external_api'):
            return 'external_api_error'
        elif 'overload' in error_str or 'busy' in error_str:
            return 'system_overload'
        
        return None
    
    def handle_error(self, 
                    error: Exception, 
                    context: Dict[str, Any] = None,
                    user_id: Optional[str] = None,
                    request_id: Optional[str] = None,
                    endpoint: Optional[str] = None) -> ErrorDetails:
        """Handle error and create detailed error information"""
        
        error_id = str(uuid.uuid4())
        context = context or {}
        
        # Identify error pattern
        pattern_key = self.identify_error_pattern(error, context)
        pattern = self.error_patterns.get(pattern_key, {})
        
        # Determine error details
        category = pattern.get('category', ErrorCategory.SYSTEM)
        severity = pattern.get('severity', ErrorSeverity.MEDIUM)
        user_message = pattern.get('user_message', 'An unexpected error occurred.')
        suggested_actions = pattern.get('suggested_actions', ['Contact support for assistance'])
        
        # Create error details
        error_details = ErrorDetails(
            error_id=error_id,
            category=category,
            severity=severity,
            message=str(error),
            user_message=user_message,
            technical_details={
                'error_type': type(error).__name__,
                'error_args': error.args,
                'pattern_matched': pattern_key
            },
            timestamp=datetime.now(),
            request_id=request_id,
            user_id=user_id,
            endpoint=endpoint,
            stack_trace=traceback.format_exc() if self.config.get('include_stack_trace', False) else None,
            context=context,
            suggested_actions=suggested_actions
        )
        
        # Store error for analysis
        self.error_history[error_id] = error_details
        
        # Log error
        self._log_error(error_details)
        
        # Send alerts for critical errors
        if severity == ErrorSeverity.CRITICAL:
            self._send_critical_alert(error_details)
        
        return error_details
    
    def _log_error(self, error_details: ErrorDetails):
        """Log error details"""
        log_data = {
            'error_id': error_details.error_id,
            'category': error_details.category.value,
            'severity': error_details.severity.value,
            'message': error_details.message,
            'user_id': error_details.user_id,
            'endpoint': error_details.endpoint,
            'context': error_details.context
        }
        
        if error_details.severity in [ErrorSeverity.HIGH, ErrorSeverity.CRITICAL]:
            self.logger.error(f"Error: {json.dumps(log_data)}")
        elif error_details.severity == ErrorSeverity.MEDIUM:
            self.logger.warning(f"Error: {json.dumps(log_data)}")
        else:
            self.logger.info(f"Error: {json.dumps(log_data)}")
    
    def _send_critical_alert(self, error_details: ErrorDetails):
        """Send alert for critical errors"""
        # This would integrate with your alerting system
        # (email, Slack, PagerDuty, etc.)
        print(f"🚨 CRITICAL ERROR ALERT: {error_details.error_id}")
        print(f"   Message: {error_details.message}")
        print(f"   Endpoint: {error_details.endpoint}")
        print(f"   User: {error_details.user_id}")
    
    def get_error_statistics(self, hours: int = 24) -> Dict[str, Any]:
        """Get error statistics for the specified time period"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_errors = [
            error for error in self.error_history.values()
            if error.timestamp >= cutoff_time
        ]
        
        # Count by category
        category_counts = {}
        for error in recent_errors:
            category = error.category.value
            category_counts[category] = category_counts.get(category, 0) + 1
        
        # Count by severity
        severity_counts = {}
        for error in recent_errors:
            severity = error.severity.value
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        # Most common errors
        error_messages = {}
        for error in recent_errors:
            msg = error.message[:100]  # Truncate for grouping
            error_messages[msg] = error_messages.get(msg, 0) + 1
        
        most_common = sorted(error_messages.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            'total_errors': len(recent_errors),
            'time_period_hours': hours,
            'by_category': category_counts,
            'by_severity': severity_counts,
            'most_common_messages': most_common,
            'error_rate_per_hour': len(recent_errors) / hours if hours > 0 else 0
        }

class UserFeedbackSystem:
    """System for collecting and managing user feedback"""
    
    def __init__(self):
        self.feedback_history: List[Dict[str, Any]] = []
        self.feedback_categories = [
            'bug_report',
            'feature_request',
            'performance_issue',
            'usability_concern',
            'general_feedback'
        ]
    
    def collect_feedback(self, 
                        user_id: str,
                        category: str,
                        message: str,
                        rating: Optional[int] = None,
                        metadata: Dict[str, Any] = None) -> str:
        """Collect user feedback"""
        feedback_id = str(uuid.uuid4())
        
        feedback = {
            'feedback_id': feedback_id,
            'user_id': user_id,
            'category': category,
            'message': message,
            'rating': rating,
            'metadata': metadata or {},
            'timestamp': datetime.now().isoformat(),
            'status': 'new'
        }
        
        self.feedback_history.append(feedback)
        
        # Log feedback
        logging.info(f"User feedback received: {feedback_id} - {category}")
        
        return feedback_id
    
    def get_feedback_summary(self, days: int = 30) -> Dict[str, Any]:
        """Get feedback summary"""
        from datetime import datetime, timedelta
        
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_feedback = [
            f for f in self.feedback_history
            if datetime.fromisoformat(f['timestamp']) >= cutoff_date
        ]
        
        # Count by category
        category_counts = {}
        for feedback in recent_feedback:
            cat = feedback['category']
            category_counts[cat] = category_counts.get(cat, 0) + 1
        
        # Average rating
        ratings = [f['rating'] for f in recent_feedback if f['rating'] is not None]
        avg_rating = sum(ratings) / len(ratings) if ratings else None
        
        return {
            'total_feedback': len(recent_feedback),
            'time_period_days': days,
            'by_category': category_counts,
            'average_rating': avg_rating,
            'total_ratings': len(ratings)
        }

def error_handler_middleware(error_handler: ErrorHandler):
    """Middleware factory for error handling"""
    def middleware(request, call_next):
        try:
            response = call_next(request)
            return response
        except Exception as e:
            # Extract context from request
            context = {
                'method': request.method,
                'url': str(request.url),
                'headers': dict(request.headers),
                'user_agent': request.headers.get('user-agent')
            }
            
            # Handle the error
            error_details = error_handler.handle_error(
                error=e,
                context=context,
                user_id=getattr(request.state, 'user_id', None),
                request_id=getattr(request.state, 'request_id', None),
                endpoint=request.url.path
            )
            
            # Return user-friendly error response
            from fastapi.responses import JSONResponse
            return JSONResponse(
                status_code=500,
                content=error_details.to_user_response()
            )
    
    return middleware

# Decorator for function-level error handling
def handle_errors(error_handler: ErrorHandler, context: Dict[str, Any] = None):
    """Decorator for handling function errors"""
    def decorator(func):
        async def async_wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                error_details = error_handler.handle_error(
                    error=e,
                    context=context or {'function': func.__name__}
                )
                raise Exception(error_details.user_message) from e
        
        def sync_wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_details = error_handler.handle_error(
                    error=e,
                    context=context or {'function': func.__name__}
                )
                raise Exception(error_details.user_message) from e
        
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator

# Example usage
if __name__ == "__main__":
    # Create error handler
    config = {
        'include_stack_trace': True,
        'log_level': 'INFO',
        'alert_critical_errors': True
    }
    
    error_handler = ErrorHandler(config)
    feedback_system = UserFeedbackSystem()
    
    print("🛠️ Enhanced Error Handling System Test")
    print("=" * 50)
    
    # Test error handling
    try:
        raise ValueError("Test validation error")
    except Exception as e:
        error_details = error_handler.handle_error(
            error=e,
            context={'test': True},
            user_id='test_user',
            endpoint='/test'
        )
        
        print(f"Error handled: {error_details.error_id}")
        print(f"User message: {error_details.user_message}")
        print(f"Suggested actions: {error_details.suggested_actions}")
    
    # Test feedback collection
    feedback_id = feedback_system.collect_feedback(
        user_id='test_user',
        category='bug_report',
        message='Found a bug in the system',
        rating=3,
        metadata={'page': 'dashboard'}
    )
    
    print(f"\nFeedback collected: {feedback_id}")
    
    # Get statistics
    stats = error_handler.get_error_statistics()
    print(f"\nError statistics: {stats}")
    
    feedback_summary = feedback_system.get_feedback_summary()
    print(f"Feedback summary: {feedback_summary}")
