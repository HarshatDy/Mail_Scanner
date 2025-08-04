"""
Email sender module using Gmail API.
Handles sending emails through Gmail API with OAuth2 authentication.
"""

from typing import Optional, List
import logging

from src.config.config_manager import get_config
from src.utils.logger import get_logger
from src.email_processing.gmail_api_connector import GmailAPIConnector


class EmailSender:
    """Email sender using Gmail API."""
    
    def __init__(self):
        self.config = get_config()
        self.logger = get_logger("email_sender")
        self.gmail_api = GmailAPIConnector()
        
    def send_email(self, 
                  to: str,
                  subject: str,
                  body: str,
                  body_type: str = 'plain',
                  cc: Optional[str] = None,
                  bcc: Optional[str] = None) -> bool:
        """
        Send an email using Gmail API.
        
        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body
            body_type: 'plain' or 'html'
            cc: CC recipient (optional)
            bcc: BCC recipient (optional)
            
        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            if self.config.email.use_gmail_api:
                return self._send_via_gmail_api(to, subject, body, body_type, cc, bcc)
            else:
                self.logger.warning("Gmail API is disabled. Please enable use_gmail_api in config.")
                return False
                
        except Exception as e:
            self.logger.error(f"Error sending email: {e}")
            return False
    
    def _send_via_gmail_api(self, 
                           to: str,
                           subject: str,
                           body: str,
                           body_type: str = 'plain',
                           cc: Optional[str] = None,
                           bcc: Optional[str] = None) -> bool:
        """Send email via Gmail API."""
        try:
            return self.gmail_api.send_email(
                to=to,
                subject=subject,
                body=body,
                body_type=body_type,
                cc=cc,
                bcc=bcc
            )
            
        except Exception as e:
            self.logger.error(f"Gmail API send error: {e}")
            return False
    
    def send_notification(self, 
                         recipient: str,
                         subject: str,
                         message: str,
                         notification_type: str = "info") -> bool:
        """
        Send a notification email.
        
        Args:
            recipient: Email address to send notification to
            subject: Email subject
            message: Notification message
            notification_type: Type of notification (info, warning, error)
            
        Returns:
            True if sent successfully, False otherwise
        """
        try:
            # Format the notification
            formatted_subject = f"[Email Scanner] {subject}"
            
            if notification_type == "error":
                formatted_subject = f"[Email Scanner - ERROR] {subject}"
            elif notification_type == "warning":
                formatted_subject = f"[Email Scanner - WARNING] {subject}"
            
            # Add notification styling
            if notification_type == "error":
                formatted_body = f"""
                <html>
                <body style="font-family: Arial, sans-serif; color: #d32f2f;">
                    <h2>⚠️ Error Notification</h2>
                    <p>{message}</p>
                    <hr>
                    <p><small>Sent by Email Scanner System</small></p>
                </body>
                </html>
                """
            elif notification_type == "warning":
                formatted_body = f"""
                <html>
                <body style="font-family: Arial, sans-serif; color: #f57c00;">
                    <h2>⚠️ Warning Notification</h2>
                    <p>{message}</p>
                    <hr>
                    <p><small>Sent by Email Scanner System</small></p>
                </body>
                </html>
                """
            else:
                formatted_body = f"""
                <html>
                <body style="font-family: Arial, sans-serif; color: #1976d2;">
                    <h2>ℹ️ Information</h2>
                    <p>{message}</p>
                    <hr>
                    <p><small>Sent by Email Scanner System</small></p>
                </body>
                </html>
                """
            
            return self.send_email(
                to=recipient,
                subject=formatted_subject,
                body=formatted_body,
                body_type='html'
            )
            
        except Exception as e:
            self.logger.error(f"Error sending notification: {e}")
            return False
    
    def send_summary_report(self, 
                          recipient: str,
                          report_data: dict) -> bool:
        """
        Send a summary report email.
        
        Args:
            recipient: Email address to send report to
            report_data: Dictionary containing report data
            
        Returns:
            True if sent successfully, False otherwise
        """
        try:
            subject = f"Email Scanner Summary Report - {report_data.get('date', 'Unknown')}"
            
            # Format the report
            html_body = self._format_summary_report(report_data)
            
            return self.send_email(
                to=recipient,
                subject=subject,
                body=html_body,
                body_type='html'
            )
            
        except Exception as e:
            self.logger.error(f"Error sending summary report: {e}")
            return False
    
    def _format_summary_report(self, report_data: dict) -> str:
        """Format summary report as HTML."""
        try:
            total_emails = report_data.get('total_emails', 0)
            processed_emails = report_data.get('processed_emails', 0)
            topics_generated = report_data.get('topics_generated', 0)
            errors = report_data.get('errors', [])
            
            html = f"""
            <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <h1 style="color: #1976d2;">📊 Email Scanner Summary Report</h1>
                
                <div style="background-color: #f5f5f5; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h2>📈 Statistics</h2>
                    <ul>
                        <li><strong>Total emails scanned:</strong> {total_emails}</li>
                        <li><strong>Emails processed:</strong> {processed_emails}</li>
                        <li><strong>Topics generated:</strong> {topics_generated}</li>
                    </ul>
                </div>
                
                <div style="background-color: #fff3e0; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h2>⚠️ Errors ({len(errors)})</h2>
                    {f'<ul>{"".join([f"<li>{error}</li>" for error in errors])}</ul>' if errors else '<p>No errors encountered.</p>'}
                </div>
                
                <hr>
                <p><small>Generated by Email Scanner System</small></p>
            </body>
            </html>
            """
            
            return html
            
        except Exception as e:
            self.logger.error(f"Error formatting summary report: {e}")
            return f"<p>Error formatting report: {e}</p>"
    
    def test_connection(self) -> bool:
        """Test the email sending connection."""
        try:
            if self.config.email.use_gmail_api:
                return self.gmail_api.test_connection()
            else:
                self.logger.warning("Gmail API is disabled. Cannot test connection.")
                return False
                
        except Exception as e:
            self.logger.error(f"Connection test failed: {e}")
            return False 