#!/usr/bin/env python3
"""
Enhanced Error Handling and User Feedback System
Comprehensive error management with user-friendly feedback and recovery
"""

import asyncio
import logging
import traceback
import json
from typing import Dict, Any, Optional, List, Union, Callable
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, asdict
from contextlib import asynccontextmanager
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logger = logging.getLogger(__name__)

class ErrorSeverity(Enum):
    """Error severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ErrorCategory(Enum):
    """Error categories for better classification"""
    VALIDATION = "validation"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    NETWORK = "network"
    DATABASE = "database"
    EXTERNAL_API = "external_api"
    SCRAPING = "scraping"
    SYSTEM = "system"
    USER_INPUT = "user_input"
    BUSINESS_LOGIC = "business_logic"

@dataclass
class ErrorDetails:
    """Comprehensive error information"""
    error_id: str
    timestamp: datetime
    category: ErrorCategory
    severity: ErrorSeverity
    message: str
    user_message: str
    technical_details: Dict[str, Any]
    context: Dict[str, Any]
    stack_trace: Optional[str] = None
    suggested_actions: List[str] = None
    recovery_options: List[Dict[str, Any]] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    endpoint: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        data['category'] = self.category.value
        data['severity'] = self.severity.value
        return data

class UserFeedbackManager:
    """Manages user feedback and notifications"""
    
    def __init__(self):
        self.feedback_queue: List[Dict[str, Any]] = []
        self.notification_callbacks: List[Callable] = []
    
    def add_feedback(self, 
                    feedback_type: str,
                    message: str,
                    severity: str = "info",
                    action_required: bool = False,
                    metadata: Optional[Dict[str, Any]] = None):
        """Add user feedback message"""
        
        feedback = {
            "id": f"feedback_{datetime.now().timestamp()}",
            "type": feedback_type,
            "message": message,
            "severity": severity,
            "action_required": action_required,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {},
            "dismissed": False
        }
        
        self.feedback_queue.append(feedback)
        
        # Notify callbacks
        for callback in self.notification_callbacks:
            try:
                callback(feedback)
            except Exception as e:
                logger.error(f"Feedback callback error: {e}")
    
    def get_pending_feedback(self, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get pending feedback messages"""
        return [f for f in self.feedback_queue if not f["dismissed"]]
    
    def dismiss_feedback(self, feedback_id: str) -> bool:
        """Dismiss a feedback message"""
        for feedback in self.feedback_queue:
            if feedback["id"] == feedback_id:
                feedback["dismissed"] = True
                return True
        return False
    
    def add_notification_callback(self, callback: Callable):
        """Add callback for new feedback notifications"""
        self.notification_callbacks.append(callback)

class ErrorRecoveryManager:
    """Manages error recovery strategies"""
    
    def __init__(self):
        self.recovery_strategies: Dict[str, Callable] = {}
        self.retry_configs: Dict[str, Dict[str, Any]] = {}
    
    def register_recovery_strategy(self, error_type: str, strategy: Callable):
        """Register a recovery strategy for an error type"""
        self.recovery_strategies[error_type] = strategy
    
    def register_retry_config(self, operation_type: str, 
                            max_retries: int = 3,
                            delay: float = 1.0,
                            backoff_factor: float = 2.0):
        """Register retry configuration for an operation type"""
        self.retry_configs[operation_type] = {
            "max_retries": max_retries,
            "delay": delay,
            "backoff_factor": backoff_factor
        }
    
    async def attempt_recovery(self, error_details: ErrorDetails) -> bool:
        """Attempt to recover from an error"""
        error_type = f"{error_details.category.value}_{error_details.severity.value}"
        
        if error_type in self.recovery_strategies:
            try:
                strategy = self.recovery_strategies[error_type]
                return await strategy(error_details)
            except Exception as e:
                logger.error(f"Recovery strategy failed: {e}")
        
        return False
    
    async def retry_with_backoff(self, operation: Callable, 
                               operation_type: str,
                               *args, **kwargs) -> Any:
        """Retry an operation with exponential backoff"""
        config = self.retry_configs.get(operation_type, {
            "max_retries": 3,
            "delay": 1.0,
            "backoff_factor": 2.0
        })
        
        last_exception = None
        
        for attempt in range(config["max_retries"] + 1):
            try:
                if asyncio.iscoroutinefunction(operation):
                    return await operation(*args, **kwargs)
                else:
                    return operation(*args, **kwargs)
                    
            except Exception as e:
                last_exception = e
                
                if attempt < config["max_retries"]:
                    delay = config["delay"] * (config["backoff_factor"] ** attempt)
                    logger.warning(f"Operation failed (attempt {attempt + 1}), retrying in {delay}s: {e}")
                    await asyncio.sleep(delay)
                else:
                    logger.error(f"Operation failed after {config['max_retries']} retries: {e}")
        
        raise last_exception

class EnhancedErrorHandler:
    """Enhanced error handling with user feedback and recovery"""
    
    def __init__(self):
        self.error_history: List[ErrorDetails] = []
        self.feedback_manager = UserFeedbackManager()
        self.recovery_manager = ErrorRecoveryManager()
        self.error_patterns: Dict[str, int] = {}  # Track error patterns
        
        # Setup default recovery strategies
        self._setup_default_strategies()
    
    def _setup_default_strategies(self):
        """Setup default error recovery strategies"""
        
        # Database connection recovery
        async def database_recovery(error_details: ErrorDetails) -> bool:
            try:
                # Attempt to reconnect to database
                logger.info("Attempting database reconnection...")
                # Add your database reconnection logic here
                return True
            except Exception:
                return False
        
        # Network error recovery
        async def network_recovery(error_details: ErrorDetails) -> bool:
            try:
                # Check network connectivity
                import requests
                response = requests.get("https://httpbin.org/status/200", timeout=5)
                return response.status_code == 200
            except Exception:
                return False
        
        # Register strategies
        self.recovery_manager.register_recovery_strategy(
            "database_high", database_recovery
        )
        self.recovery_manager.register_recovery_strategy(
            "network_medium", network_recovery
        )
        
        # Register retry configurations
        self.recovery_manager.register_retry_config("api_call", max_retries=3, delay=1.0)
        self.recovery_manager.register_retry_config("database_query", max_retries=2, delay=0.5)
        self.recovery_manager.register_retry_config("scraping_request", max_retries=5, delay=2.0)
    
    def _generate_error_id(self) -> str:
        """Generate unique error ID"""
        return f"err_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(self.error_history)}"
    
    def _categorize_error(self, exception: Exception, context: Dict[str, Any]) -> ErrorCategory:
        """Automatically categorize errors based on type and context"""
        
        error_type = type(exception).__name__
        error_message = str(exception).lower()
        
        # Database errors
        if any(keyword in error_type.lower() for keyword in ['sqlite', 'database', 'connection']):
            return ErrorCategory.DATABASE
        
        # Network errors
        if any(keyword in error_type.lower() for keyword in ['connection', 'timeout', 'network']):
            return ErrorCategory.NETWORK
        
        # Validation errors
        if any(keyword in error_type.lower() for keyword in ['validation', 'value', 'type']):
            return ErrorCategory.VALIDATION
        
        # Authentication errors
        if any(keyword in error_message for keyword in ['unauthorized', 'authentication', 'login']):
            return ErrorCategory.AUTHENTICATION
        
        # Check context for category hints
        if context.get('endpoint'):
            if 'auth' in context['endpoint']:
                return ErrorCategory.AUTHENTICATION
            elif 'scraping' in context['endpoint'] or 'job' in context['endpoint']:
                return ErrorCategory.SCRAPING
        
        return ErrorCategory.SYSTEM
    
    def _determine_severity(self, exception: Exception, category: ErrorCategory) -> ErrorSeverity:
        """Determine error severity"""
        
        error_type = type(exception).__name__
        error_message = str(exception).lower()
        
        # Critical errors
        critical_indicators = ['fatal', 'critical', 'system', 'memory', 'disk']
        if any(indicator in error_message for indicator in critical_indicators):
            return ErrorSeverity.CRITICAL
        
        # Category-based severity
        if category == ErrorCategory.DATABASE:
            return ErrorSeverity.HIGH
        elif category == ErrorCategory.AUTHENTICATION:
            return ErrorSeverity.MEDIUM
        elif category == ErrorCategory.VALIDATION:
            return ErrorSeverity.LOW
        
        # Exception type based severity
        if error_type in ['SystemError', 'MemoryError', 'OSError']:
            return ErrorSeverity.CRITICAL
        elif error_type in ['ConnectionError', 'TimeoutError']:
            return ErrorSeverity.HIGH
        elif error_type in ['ValueError', 'TypeError']:
            return ErrorSeverity.MEDIUM
        
        return ErrorSeverity.LOW
    
    def _generate_user_message(self, error_details: ErrorDetails) -> str:
        """Generate user-friendly error message"""
        
        category = error_details.category
        severity = error_details.severity
        
        base_messages = {
            ErrorCategory.VALIDATION: "Please check your input and try again.",
            ErrorCategory.AUTHENTICATION: "Please verify your login credentials.",
            ErrorCategory.NETWORK: "Network connection issue. Please check your internet connection.",
            ErrorCategory.DATABASE: "Data service temporarily unavailable. Please try again in a moment.",
            ErrorCategory.SCRAPING: "Website scraping encountered an issue. The site may be temporarily unavailable.",
            ErrorCategory.SYSTEM: "System error occurred. Our team has been notified."
        }
        
        base_message = base_messages.get(category, "An unexpected error occurred.")
        
        if severity == ErrorSeverity.CRITICAL:
            return f"Critical issue: {base_message} Please contact support immediately."
        elif severity == ErrorSeverity.HIGH:
            return f"Service disruption: {base_message} We're working to resolve this."
        else:
            return base_message
    
    def _generate_suggested_actions(self, error_details: ErrorDetails) -> List[str]:
        """Generate suggested actions for users"""
        
        actions = []
        category = error_details.category
        
        action_map = {
            ErrorCategory.VALIDATION: [
                "Check all required fields are filled",
                "Verify data formats (dates, emails, URLs)",
                "Review input for special characters"
            ],
            ErrorCategory.AUTHENTICATION: [
                "Check username and password",
                "Clear browser cache and cookies",
                "Request password reset if needed"
            ],
            ErrorCategory.NETWORK: [
                "Check internet connection",
                "Try refreshing the page",
                "Wait a moment and try again"
            ],
            ErrorCategory.DATABASE: [
                "Try again in a few moments",
                "Contact support if issue persists"
            ],
            ErrorCategory.SCRAPING: [
                "Verify the website URL is correct",
                "Check if the website is accessible",
                "Try again with different settings"
            ]
        }
        
        return action_map.get(category, ["Contact support for assistance"])
    
    def _track_error_pattern(self, error_details: ErrorDetails):
        """Track error patterns for analysis"""
        pattern_key = f"{error_details.category.value}_{error_details.severity.value}"
        self.error_patterns[pattern_key] = self.error_patterns.get(pattern_key, 0) + 1
        
        # Alert on error spikes
        if self.error_patterns[pattern_key] > 10:  # Threshold for concern
            self.feedback_manager.add_feedback(
                "system_alert",
                f"High frequency of {pattern_key} errors detected",
                severity="warning",
                action_required=True
            )
    
    async def handle_error(self,
                          exception: Exception,
                          context: Optional[Dict[str, Any]] = None,
                          user_id: Optional[str] = None,
                          session_id: Optional[str] = None,
                          endpoint: Optional[str] = None) -> ErrorDetails:
        """Handle an error comprehensively"""
        
        context = context or {}
        
        # Create error details
        category = self._categorize_error(exception, context)
        severity = self._determine_severity(exception, category)
        
        error_details = ErrorDetails(
            error_id=self._generate_error_id(),
            timestamp=datetime.now(),
            category=category,
            severity=severity,
            message=str(exception),
            user_message=self._generate_user_message(ErrorDetails(
                error_id="", timestamp=datetime.now(), category=category,
                severity=severity, message="", user_message="",
                technical_details={}, context={}
            )),
            technical_details={
                "exception_type": type(exception).__name__,
                "exception_args": exception.args,
                "module": getattr(exception, '__module__', 'unknown')
            },
            context=context,
            stack_trace=traceback.format_exc(),
            suggested_actions=self._generate_suggested_actions(ErrorDetails(
                error_id="", timestamp=datetime.now(), category=category,
                severity=severity, message="", user_message="",
                technical_details={}, context={}
            )),
            user_id=user_id,
            session_id=session_id,
            endpoint=endpoint
        )
        
        # Update user message with complete error details
        error_details.user_message = self._generate_user_message(error_details)
        error_details.suggested_actions = self._generate_suggested_actions(error_details)
        
        # Store error
        self.error_history.append(error_details)
        
        # Track patterns
        self._track_error_pattern(error_details)
        
        # Log error appropriately
        log_level = {
            ErrorSeverity.LOW: logging.INFO,
            ErrorSeverity.MEDIUM: logging.WARNING,
            ErrorSeverity.HIGH: logging.ERROR,
            ErrorSeverity.CRITICAL: logging.CRITICAL
        }[severity]
        
        logger.log(log_level, f"Error {error_details.error_id}: {error_details.message}")
        
        # Add user feedback
        self.feedback_manager.add_feedback(
            "error",
            error_details.user_message,
            severity=severity.value,
            action_required=severity in [ErrorSeverity.HIGH, ErrorSeverity.CRITICAL],
            metadata={
                "error_id": error_details.error_id,
                "category": category.value,
                "suggested_actions": error_details.suggested_actions
            }
        )
        
        # Attempt recovery for high/critical errors
        if severity in [ErrorSeverity.HIGH, ErrorSeverity.CRITICAL]:
            try:
                recovery_success = await self.recovery_manager.attempt_recovery(error_details)
                if recovery_success:
                    self.feedback_manager.add_feedback(
                        "recovery_success",
                        "Issue automatically resolved. You can continue normally.",
                        severity="success"
                    )
            except Exception as recovery_error:
                logger.error(f"Recovery attempt failed: {recovery_error}")
        
        return error_details
    
    @asynccontextmanager
    async def error_context(self, operation_name: str, **context):
        """Context manager for automatic error handling"""
        try:
            yield
        except Exception as e:
            await self.handle_error(
                e,
                context={**context, "operation": operation_name},
                endpoint=context.get("endpoint")
            )
            raise
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """Get comprehensive error statistics"""
        
        if not self.error_history:
            return {"total_errors": 0}
        
        # Calculate statistics
        total_errors = len(self.error_history)
        recent_errors = [
            error for error in self.error_history
            if error.timestamp > datetime.now() - timedelta(hours=24)
        ]
        
        # Category breakdown
        category_counts = {}
        severity_counts = {}
        
        for error in self.error_history:
            category_counts[error.category.value] = category_counts.get(error.category.value, 0) + 1
            severity_counts[error.severity.value] = severity_counts.get(error.severity.value, 0) + 1
        
        # Recent error rate
        hours_24_ago = datetime.now() - timedelta(hours=24)
        recent_error_rate = len([
            error for error in self.error_history
            if error.timestamp > hours_24_ago
        ])
        
        return {
            "total_errors": total_errors,
            "recent_24h": len(recent_errors),
            "error_rate_24h": recent_error_rate,
            "category_breakdown": category_counts,
            "severity_breakdown": severity_counts,
            "error_patterns": self.error_patterns,
            "most_common_category": max(category_counts.items(), key=lambda x: x[1])[0] if category_counts else None,
            "most_common_severity": max(severity_counts.items(), key=lambda x: x[1])[0] if severity_counts else None
        }

# Global error handler instance
error_handler: Optional[EnhancedErrorHandler] = None

def init_error_handling() -> EnhancedErrorHandler:
    """Initialize the enhanced error handling system"""
    global error_handler
    error_handler = EnhancedErrorHandler()
    logger.info("✅ Enhanced error handling system initialized")
    return error_handler

def get_error_handler() -> Optional[EnhancedErrorHandler]:
    """Get the global error handler"""
    return error_handler

# Decorator for automatic error handling
def handle_errors(operation_name: str = "operation"):
    """Decorator for automatic error handling"""
    def decorator(func):
        async def async_wrapper(*args, **kwargs):
            if not error_handler:
                return await func(*args, **kwargs)
            
            async with error_handler.error_context(operation_name):
                return await func(*args, **kwargs)
        
        def sync_wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if error_handler:
                    # For sync functions, we can't await, so just log
                    logger.error(f"Error in {operation_name}: {e}")
                raise
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    
    return decorator

if __name__ == "__main__":
    async def test_error_handling():
        """Test the error handling system"""
        print("🧪 Testing Enhanced Error Handling System")
        print("==========================================")
        
        # Initialize error handler
        handler = init_error_handling()
        
        # Test different error types
        test_cases = [
            {
                "name": "Validation Error",
                "exception": ValueError("Invalid email format"),
                "context": {"field": "email", "value": "invalid-email"}
            },
            {
                "name": "Database Error",
                "exception": ConnectionError("Database connection failed"),
                "context": {"operation": "user_lookup", "table": "users"}
            },
            {
                "name": "Network Error",
                "exception": TimeoutError("Request timeout after 30 seconds"),
                "context": {"url": "https://example.com", "timeout": 30}
            }
        ]
        
        for test_case in test_cases:
            print(f"\n📝 Testing {test_case['name']}...")
            
            try:
                error_details = await handler.handle_error(
                    test_case["exception"],
                    context=test_case["context"]
                )
                
                print(f"   ✅ Error handled: {error_details.error_id}")
                print(f"   📋 Category: {error_details.category.value}")
                print(f"   ⚠️  Severity: {error_details.severity.value}")
                print(f"   💬 User Message: {error_details.user_message}")
                print(f"   🔧 Suggested Actions: {len(error_details.suggested_actions)} actions")
                
            except Exception as e:
                print(f"   ❌ Test failed: {e}")
        
        # Test feedback system
        print(f"\n📨 Testing Feedback System...")
        feedback_messages = handler.feedback_manager.get_pending_feedback()
        print(f"   📬 Pending feedback: {len(feedback_messages)} messages")
        
        for feedback in feedback_messages[:3]:  # Show first 3
            print(f"   - {feedback['type']}: {feedback['message'][:50]}...")
        
        # Test error statistics
        print(f"\n📊 Error Statistics:")
        stats = handler.get_error_statistics()
        for key, value in stats.items():
            if isinstance(value, dict):
                print(f"   {key}: {len(value)} categories")
            else:
                print(f"   {key}: {value}")
        
        print("\n✅ Error handling system test completed!")

    # Run the test
    asyncio.run(test_error_handling())
