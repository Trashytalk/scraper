"""
Notification Handlers for Monitoring System
Provides multiple notification channels for alerts and monitoring events
"""

import asyncio
import logging
import smtplib
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from abc import ABC, abstractmethod
import aiohttp
from dataclasses import dataclass

from ..db.centralized_data import AlertRecord


logger = logging.getLogger(__name__)


@dataclass
class NotificationConfig:
    """Configuration for notification channels"""
    enabled: bool = True
    rate_limit_minutes: int = 15  # Minimum time between similar notifications
    retry_attempts: int = 3
    timeout_seconds: int = 30


class NotificationHandler(ABC):
    """Base class for notification handlers"""
    
    def __init__(self, config: NotificationConfig):
        self.config = config
        self.last_notifications = {}  # Track last notification times for rate limiting
    
    @abstractmethod
    async def send_notification(self, alert: AlertRecord, custom_data: Dict[str, Any] = None) -> bool:
        """Send a notification for an alert"""
        pass
    
    def should_rate_limit(self, alert: AlertRecord) -> bool:
        """Check if notification should be rate limited"""
        if not self.config.enabled:
            return True
            
        rate_limit_key = f"{alert.category}_{alert.severity}"
        last_time = self.last_notifications.get(rate_limit_key)
        
        if last_time:
            time_diff = (datetime.utcnow() - last_time).total_seconds() / 60
            if time_diff < self.config.rate_limit_minutes:
                return True
        
        self.last_notifications[rate_limit_key] = datetime.utcnow()
        return False
    
    def format_alert_message(self, alert: AlertRecord) -> Dict[str, str]:
        """Format alert data for notifications"""
        return {
            "title": f"🚨 {alert.severity.upper()}: {alert.title}",
            "body": alert.message,
            "details": f"""
Alert Details:
- Severity: {alert.severity.upper()}
- Category: {alert.category}
- Component: {alert.source_component}
- Triggered: {alert.triggered_at.strftime('%Y-%m-%d %H:%M:%S UTC')}
- Metric: {alert.source_metric_name} = {alert.source_metric_value}
- Threshold: {alert.threshold_value}

{alert.message}

Alert ID: {alert.alert_uuid}
            """.strip(),
            "short_text": f"{alert.category}: {alert.source_metric_name} = {alert.source_metric_value}"
        }


class EmailNotificationHandler(NotificationHandler):
    """Email notification handler"""
    
    def __init__(self, config: NotificationConfig, email_config: Dict[str, Any]):
        super().__init__(config)
        self.smtp_server = email_config.get("smtp_server", "localhost")
        self.smtp_port = email_config.get("smtp_port", 587)
        self.smtp_username = email_config.get("smtp_username")
        self.smtp_password = email_config.get("smtp_password")
        self.use_tls = email_config.get("use_tls", True)
        self.from_email = email_config.get("from_email", "monitoring@example.com")
        self.to_emails = email_config.get("to_emails", [])
        
    async def send_notification(self, alert: AlertRecord, custom_data: Dict[str, Any] = None) -> bool:
        """Send email notification"""
        if self.should_rate_limit(alert):
            logger.debug(f"Email notification rate limited for alert {alert.alert_uuid}")
            return False
        
        try:
            formatted = self.format_alert_message(alert)
            
            # Create email message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = formatted["title"]
            msg['From'] = self.from_email
            msg['To'] = ', '.join(self.to_emails)
            
            # Create HTML and text versions
            html_body = self._create_html_email(alert, formatted)
            text_body = formatted["details"]
            
            msg.attach(MIMEText(text_body, 'plain'))
            msg.attach(MIMEText(html_body, 'html'))
            
            # Send email
            await self._send_email_async(msg)
            
            logger.info(f"Email notification sent for alert {alert.alert_uuid}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email notification: {e}")
            return False
    
    def _create_html_email(self, alert: AlertRecord, formatted: Dict[str, str]) -> str:
        """Create HTML email content"""
        severity_colors = {
            "critical": "#dc3545",
            "high": "#fd7e14", 
            "medium": "#ffc107",
            "low": "#28a745"
        }
        
        color = severity_colors.get(alert.severity, "#6c757d")
        
        return f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="background-color: {color}; color: white; padding: 15px; border-radius: 5px; margin-bottom: 20px;">
                    <h2 style="margin: 0;">🚨 {alert.severity.upper()} Alert</h2>
                    <p style="margin: 5px 0 0 0; font-size: 18px;">{alert.title}</p>
                </div>
                
                <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin-bottom: 15px;">
                    <p style="margin: 0;"><strong>Message:</strong> {alert.message}</p>
                </div>
                
                <table style="width: 100%; border-collapse: collapse; margin-bottom: 15px;">
                    <tr style="background-color: #e9ecef;">
                        <td style="padding: 8px; border: 1px solid #dee2e6;"><strong>Category</strong></td>
                        <td style="padding: 8px; border: 1px solid #dee2e6;">{alert.category}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; border: 1px solid #dee2e6;"><strong>Component</strong></td>
                        <td style="padding: 8px; border: 1px solid #dee2e6;">{alert.source_component}</td>
                    </tr>
                    <tr style="background-color: #e9ecef;">
                        <td style="padding: 8px; border: 1px solid #dee2e6;"><strong>Metric</strong></td>
                        <td style="padding: 8px; border: 1px solid #dee2e6;">{alert.source_metric_name}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; border: 1px solid #dee2e6;"><strong>Value</strong></td>
                        <td style="padding: 8px; border: 1px solid #dee2e6;">{alert.source_metric_value}</td>
                    </tr>
                    <tr style="background-color: #e9ecef;">
                        <td style="padding: 8px; border: 1px solid #dee2e6;"><strong>Threshold</strong></td>
                        <td style="padding: 8px; border: 1px solid #dee2e6;">{alert.threshold_value}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; border: 1px solid #dee2e6;"><strong>Triggered</strong></td>
                        <td style="padding: 8px; border: 1px solid #dee2e6;">{alert.triggered_at.strftime('%Y-%m-%d %H:%M:%S UTC')}</td>
                    </tr>
                </table>
                
                <div style="background-color: #f1f3f4; padding: 10px; border-radius: 3px; font-size: 12px; color: #6c757d;">
                    <p style="margin: 0;"><strong>Alert ID:</strong> {alert.alert_uuid}</p>
                    <p style="margin: 5px 0 0 0;">This is an automated notification from the Business Intelligence Scraper monitoring system.</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    async def _send_email_async(self, msg: MIMEMultipart):
        """Send email asynchronously"""
        def send_email():
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                if self.use_tls:
                    server.starttls()
                if self.smtp_username and self.smtp_password:
                    server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
        
        # Run in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, send_email)


class SlackNotificationHandler(NotificationHandler):
    """Slack notification handler"""
    
    def __init__(self, config: NotificationConfig, slack_config: Dict[str, Any]):
        super().__init__(config)
        self.webhook_url = slack_config.get("webhook_url")
        self.channel = slack_config.get("channel", "#monitoring")
        self.username = slack_config.get("username", "MonitoringBot")
        self.icon_emoji = slack_config.get("icon_emoji", ":warning:")
    
    async def send_notification(self, alert: AlertRecord, custom_data: Dict[str, Any] = None) -> bool:
        """Send Slack notification"""
        if self.should_rate_limit(alert):
            logger.debug(f"Slack notification rate limited for alert {alert.alert_uuid}")
            return False
        
        if not self.webhook_url:
            logger.warning("Slack webhook URL not configured")
            return False
        
        try:
            formatted = self.format_alert_message(alert)
            
            # Create Slack message
            slack_message = self._create_slack_message(alert, formatted)
            
            # Send to Slack
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.webhook_url,
                    json=slack_message,
                    timeout=aiohttp.ClientTimeout(total=self.config.timeout_seconds)
                ) as response:
                    if response.status == 200:
                        logger.info(f"Slack notification sent for alert {alert.alert_uuid}")
                        return True
                    else:
                        logger.error(f"Slack notification failed with status {response.status}")
                        return False
        
        except Exception as e:
            logger.error(f"Failed to send Slack notification: {e}")
            return False
    
    def _create_slack_message(self, alert: AlertRecord, formatted: Dict[str, str]) -> Dict[str, Any]:
        """Create Slack message payload"""
        severity_colors = {
            "critical": "danger",
            "high": "warning",
            "medium": "warning", 
            "low": "good"
        }
        
        color = severity_colors.get(alert.severity, "warning")
        
        return {
            "channel": self.channel,
            "username": self.username,
            "icon_emoji": self.icon_emoji,
            "attachments": [
                {
                    "color": color,
                    "title": f"{alert.severity.upper()} Alert: {alert.title}",
                    "text": alert.message,
                    "fields": [
                        {
                            "title": "Category",
                            "value": alert.category,
                            "short": True
                        },
                        {
                            "title": "Component", 
                            "value": alert.source_component,
                            "short": True
                        },
                        {
                            "title": "Metric",
                            "value": f"{alert.source_metric_name} = {alert.source_metric_value}",
                            "short": True
                        },
                        {
                            "title": "Threshold",
                            "value": str(alert.threshold_value),
                            "short": True
                        }
                    ],
                    "footer": "Business Intelligence Scraper Monitoring",
                    "ts": int(alert.triggered_at.timestamp())
                }
            ]
        }


class WebhookNotificationHandler(NotificationHandler):
    """Generic webhook notification handler"""
    
    def __init__(self, config: NotificationConfig, webhook_config: Dict[str, Any]):
        super().__init__(config)
        self.webhook_url = webhook_config.get("webhook_url")
        self.headers = webhook_config.get("headers", {"Content-Type": "application/json"})
        self.auth_token = webhook_config.get("auth_token")
        
        if self.auth_token:
            self.headers["Authorization"] = f"Bearer {self.auth_token}"
    
    async def send_notification(self, alert: AlertRecord, custom_data: Dict[str, Any] = None) -> bool:
        """Send webhook notification"""
        if self.should_rate_limit(alert):
            logger.debug(f"Webhook notification rate limited for alert {alert.alert_uuid}")
            return False
        
        if not self.webhook_url:
            logger.warning("Webhook URL not configured")
            return False
        
        try:
            # Create webhook payload
            payload = {
                "alert_id": alert.alert_uuid,
                "severity": alert.severity,
                "category": alert.category,
                "title": alert.title,
                "message": alert.message,
                "source_component": alert.source_component,
                "source_metric_name": alert.source_metric_name,
                "source_metric_value": alert.source_metric_value,
                "threshold_value": alert.threshold_value,
                "triggered_at": alert.triggered_at.isoformat(),
                "technical_details": alert.technical_details,
                "custom_data": custom_data or {}
            }
            
            # Send webhook
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.webhook_url,
                    json=payload,
                    headers=self.headers,
                    timeout=aiohttp.ClientTimeout(total=self.config.timeout_seconds)
                ) as response:
                    if 200 <= response.status < 300:
                        logger.info(f"Webhook notification sent for alert {alert.alert_uuid}")
                        return True
                    else:
                        logger.error(f"Webhook notification failed with status {response.status}")
                        return False
        
        except Exception as e:
            logger.error(f"Failed to send webhook notification: {e}")
            return False


class ConsoleNotificationHandler(NotificationHandler):
    """Console/log notification handler for development and debugging"""
    
    def __init__(self, config: NotificationConfig):
        super().__init__(config)
    
    async def send_notification(self, alert: AlertRecord, custom_data: Dict[str, Any] = None) -> bool:
        """Send console notification (log to console)"""
        if self.should_rate_limit(alert):
            return False
        
        try:
            formatted = self.format_alert_message(alert)
            
            # Log to console with formatting
            print("\n" + "="*80)
            print(formatted["title"])
            print("="*80)
            print(formatted["details"])
            if custom_data:
                print(f"\nCustom Data: {json.dumps(custom_data, indent=2)}")
            print("="*80 + "\n")
            
            # Also log to logger
            logger.warning(f"ALERT: {formatted['title']} - {formatted['short_text']}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to send console notification: {e}")
            return False


class NotificationManager:
    """Manages multiple notification handlers"""
    
    def __init__(self):
        self.handlers: Dict[str, NotificationHandler] = {}
        self.default_config = NotificationConfig()
    
    def register_handler(self, name: str, handler: NotificationHandler):
        """Register a notification handler"""
        self.handlers[name] = handler
        logger.info(f"Registered notification handler: {name}")
    
    def remove_handler(self, name: str):
        """Remove a notification handler"""
        if name in self.handlers:
            del self.handlers[name]
            logger.info(f"Removed notification handler: {name}")
    
    async def send_notifications(self, alert: AlertRecord, channels: List[str] = None, custom_data: Dict[str, Any] = None):
        """Send notifications through specified channels"""
        if channels is None:
            channels = list(self.handlers.keys())
        
        results = {}
        
        for channel in channels:
            if channel in self.handlers:
                try:
                    success = await self.handlers[channel].send_notification(alert, custom_data)
                    results[channel] = {"success": success, "error": None}
                except Exception as e:
                    results[channel] = {"success": False, "error": str(e)}
                    logger.error(f"Error sending notification via {channel}: {e}")
            else:
                results[channel] = {"success": False, "error": f"Handler not found: {channel}"}
                logger.warning(f"Notification handler not found: {channel}")
        
        return results
    
    def setup_default_handlers(self, config: Dict[str, Any]):
        """Setup default notification handlers from configuration"""
        
        # Setup email handler
        if config.get("email", {}).get("enabled", False):
            email_config = config["email"]
            self.register_handler(
                "email",
                EmailNotificationHandler(self.default_config, email_config)
            )
        
        # Setup Slack handler
        if config.get("slack", {}).get("enabled", False):
            slack_config = config["slack"]
            self.register_handler(
                "slack", 
                SlackNotificationHandler(self.default_config, slack_config)
            )
        
        # Setup webhook handler
        if config.get("webhook", {}).get("enabled", False):
            webhook_config = config["webhook"]
            self.register_handler(
                "webhook",
                WebhookNotificationHandler(self.default_config, webhook_config)
            )
        
        # Always setup console handler for development
        self.register_handler(
            "console",
            ConsoleNotificationHandler(self.default_config)
        )
    
    def get_handler_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all registered handlers"""
        status = {}
        for name, handler in self.handlers.items():
            status[name] = {
                "enabled": handler.config.enabled,
                "rate_limit_minutes": handler.config.rate_limit_minutes,
                "last_notifications_count": len(handler.last_notifications)
            }
        return status


# Global notification manager instance
notification_manager = NotificationManager()


# Convenience function for external use
async def send_alert_notifications(alert: AlertRecord, channels: List[str] = None, custom_data: Dict[str, Any] = None):
    """Send alert notifications through specified channels"""
    return await notification_manager.send_notifications(alert, channels, custom_data)
