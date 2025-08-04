"""
Gmail email connector for the Email Scanner system.
Handles both IMAP connections and Gmail API with OAuth2 authentication.
"""

import imaplib
import email
import ssl
# Using built-in email module
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Any, Optional, Tuple
import logging
from datetime import datetime, timedelta

from src.config.config_manager import get_config
from src.utils.logger import get_logger
from src.email_processing.gmail_api_connector import GmailAPIConnector


class GmailConnector:
    """Gmail-specific email connector with OAuth2 support."""
    
    def __init__(self):
        self.config = get_config()
        self.logger = get_logger("gmail_connector")
        self.imap_connection: Optional[imaplib.IMAP4_SSL] = None
        self.smtp_connection = None
        self.gmail_api = GmailAPIConnector() if self.config.email.use_gmail_api else None
        
    def connect(self) -> bool:
        """Establish connection to Gmail (IMAP or API)."""
        if self.config.email.use_gmail_api:
            return self.gmail_api.authenticate()
        else:
            return self._connect_imap()
    
    def _connect_imap(self) -> bool:
        """Establish connection to Gmail IMAP server."""
        try:
            # Create SSL context for secure connection
            ssl_context = ssl.create_default_context()
            
            # Connect to Gmail IMAP server
            self.imap_connection = imaplib.IMAP4_SSL(
                self.config.email.imap_server,
                self.config.email.imap_port,
                ssl_context=ssl_context
            )
            
            # Login with username and app password
            self.imap_connection.login(
                self.config.email.username,
                self.config.email.password
            )
            
            self.logger.info(f"Successfully connected to Gmail IMAP as {self.config.email.username}")
            return True
            
        except imaplib.IMAP4.error as e:
            self.logger.error(f"IMAP authentication failed: {e}")
            return False
        except Exception as e:
            self.logger.error(f"IMAP connection failed: {e}")
            return False
    
    def disconnect(self):
        """Close the connection (IMAP or API)."""
        if self.config.email.use_gmail_api:
            # Gmail API doesn't require explicit disconnection
            self.logger.info("Gmail API connection closed")
        elif self.imap_connection:
            try:
                self.imap_connection.logout()
                self.logger.info("IMAP connection closed")
            except Exception as e:
                self.logger.error(f"Error closing IMAP connection: {e}")
            finally:
                self.imap_connection = None
    
    def get_email_count(self, folder: str = "INBOX") -> int:
        """Get the number of emails in a folder."""
        if self.config.email.use_gmail_api:
            return self.gmail_api.get_email_count(f"in:{folder.lower()}")
        else:
            try:
                self.imap_connection.select(folder)
                _, messages = self.imap_connection.search(None, "ALL")
                return len(messages[0].split())
            except Exception as e:
                self.logger.error(f"Error getting email count: {e}")
                return 0
    
    def fetch_emails(self, 
                    folder: str = "INBOX", 
                    limit: int = 50, 
                    days_back: int = 7,
                    unread_only: bool = False) -> List[Dict[str, Any]]:
        """
        Fetch emails from Gmail with filtering options.
        
        Args:
            folder: Email folder to search (default: INBOX)
            limit: Maximum number of emails to fetch
            days_back: Number of days back to search
            unread_only: Only fetch unread emails
            
        Returns:
            List of email dictionaries with metadata and content
        """
        if self.config.email.use_gmail_api:
            return self.gmail_api.fetch_emails(
                query=f"in:{folder.lower()}",
                limit=limit,
                days_back=days_back,
                unread_only=unread_only
            )
        else:
            return self._fetch_emails_imap(folder, limit, days_back, unread_only)
    
    def _fetch_emails_imap(self, 
                          folder: str = "INBOX", 
                          limit: int = 50, 
                          days_back: int = 7,
                          unread_only: bool = False) -> List[Dict[str, Any]]:
        """Fetch emails using IMAP."""
        emails = []
        
        try:
            # Select the folder
            self.imap_connection.select(folder)
            
            # Build search criteria
            search_criteria = []
            
            if unread_only:
                search_criteria.append("UNSEEN")
            
            # Add date filter
            if days_back > 0:
                date_since = (datetime.now() - timedelta(days=days_back)).strftime("%d-%b-%Y")
                search_criteria.append(f'SINCE "{date_since}"')
            
            search_string = " ".join(search_criteria) if search_criteria else "ALL"
            
            # Search for emails
            _, message_numbers = self.imap_connection.search(None, search_string)
            
            if not message_numbers[0]:
                self.logger.info("No emails found matching criteria")
                return emails
            
            # Get the most recent emails (limit)
            email_list = message_numbers[0].split()
            if limit:
                email_list = email_list[-limit:]  # Get the most recent emails
            
            self.logger.info(f"Found {len(email_list)} emails to process")
            
            # Fetch each email
            for num in email_list:
                try:
                    email_data = self._fetch_single_email(num)
                    if email_data:
                        emails.append(email_data)
                except Exception as e:
                    self.logger.error(f"Error fetching email {num}: {e}")
                    continue
            
            return emails
            
        except Exception as e:
            self.logger.error(f"Error fetching emails: {e}")
            return emails
    
    def _fetch_single_email(self, email_num: bytes) -> Optional[Dict[str, Any]]:
        """Fetch a single email by its number."""
        try:
            # Fetch the email
            _, msg_data = self.imap_connection.fetch(email_num, "(RFC822)")
            email_body = msg_data[0][1]
            
            # Parse the email
            email_message = email.message_from_bytes(email_body)
            
            # Extract email data
            email_data = {
                'uid': email_num.decode(),
                'subject': self._decode_header(email_message.get('Subject', '')),
                'from': self._decode_header(email_message.get('From', '')),
                'to': self._decode_header(email_message.get('To', '')),
                'date': email_message.get('Date', ''),
                'message_id': email_message.get('Message-ID', ''),
                'content_type': email_message.get_content_type(),
                'body': self._extract_body(email_message),
                'headers': dict(email_message.items()),
                'attachments': self._extract_attachments(email_message)
            }
            
            return email_data
            
        except Exception as e:
            self.logger.error(f"Error parsing email {email_num}: {e}")
            return None
    
    def _decode_header(self, header: str) -> str:
        """Decode email headers properly."""
        if not header:
            return ""
        
        try:
            # Handle encoded headers
            decoded_parts = email.header.decode_header(header)
            decoded_string = ""
            
            for part, encoding in decoded_parts:
                if isinstance(part, bytes):
                    if encoding:
                        decoded_string += part.decode(encoding)
                    else:
                        decoded_string += part.decode('utf-8', errors='ignore')
                else:
                    decoded_string += str(part)
            
            return decoded_string
        except Exception:
            return str(header)
    
    def _extract_body(self, email_message) -> str:
        """Extract the text body from an email message."""
        body = ""
        
        if email_message.is_multipart():
            for part in email_message.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))
                
                # Skip attachments
                if "attachment" in content_disposition:
                    continue
                
                # Get text content
                if content_type == "text/plain":
                    try:
                        body += part.get_payload(decode=True).decode('utf-8', errors='ignore')
                    except Exception:
                        body += part.get_payload(decode=True).decode('latin-1', errors='ignore')
                elif content_type == "text/html" and not body:
                    # Use HTML if no plain text available
                    try:
                        body += part.get_payload(decode=True).decode('utf-8', errors='ignore')
                    except Exception:
                        body += part.get_payload(decode=True).decode('latin-1', errors='ignore')
        else:
            # Not multipart
            try:
                body = email_message.get_payload(decode=True).decode('utf-8', errors='ignore')
            except Exception:
                body = email_message.get_payload(decode=True).decode('latin-1', errors='ignore')
        
        return body.strip()
    
    def _extract_attachments(self, email_message) -> List[Dict[str, Any]]:
        """Extract attachment information from email."""
        attachments = []
        
        if email_message.is_multipart():
            for part in email_message.walk():
                content_disposition = str(part.get("Content-Disposition"))
                
                if "attachment" in content_disposition:
                    filename = part.get_filename()
                    if filename:
                        attachments.append({
                            'filename': self._decode_header(filename),
                            'content_type': part.get_content_type(),
                            'size': len(part.get_payload(decode=True)) if part.get_payload(decode=True) else 0
                        })
        
        return attachments
    
    def mark_as_read(self, email_uids: List[str], folder: str = "INBOX") -> bool:
        """Mark emails as read."""
        if self.config.email.use_gmail_api:
            return self.gmail_api.mark_as_read(email_uids)
        else:
            try:
                self.imap_connection.select(folder)
                
                for uid in email_uids:
                    self.imap_connection.store(uid, '+FLAGS', '\\Seen')
                
                self.logger.info(f"Marked {len(email_uids)} emails as read")
                return True
                
            except Exception as e:
                self.logger.error(f"Error marking emails as read: {e}")
                return False
    
    def move_to_folder(self, email_uids: List[str], source_folder: str, target_folder: str) -> bool:
        """Move emails to a different folder."""
        if self.config.email.use_gmail_api:
            return self.gmail_api.add_label(email_uids, target_folder)
        else:
            try:
                self.imap_connection.select(source_folder)
                
                for uid in email_uids:
                    self.imap_connection.store(uid, '+X-GM-LABELS', target_folder)
                
                self.logger.info(f"Moved {len(email_uids)} emails to {target_folder}")
                return True
                
            except Exception as e:
                self.logger.error(f"Error moving emails: {e}")
                return False
    
    def get_folders(self) -> List[str]:
        """Get list of available folders/labels."""
        if self.config.email.use_gmail_api:
            labels = self.gmail_api.get_labels()
            return [label['name'] for label in labels if label['type'] == 'user']
        else:
            try:
                _, folders = self.imap_connection.list()
                folder_names = []
                
                for folder in folders:
                    folder_name = folder.decode().split('"')[-2]
                    if folder_name:
                        folder_names.append(folder_name)
                
                return folder_names
                
            except Exception as e:
                self.logger.error(f"Error getting folders: {e}")
                return []
    
    def test_connection(self) -> bool:
        """Test the Gmail connection and authentication."""
        try:
            if self.config.email.use_gmail_api:
                return self.gmail_api.test_connection()
            else:
                if not self.connect():
                    return False
                
                # Try to get email count as a test
                count = self.get_email_count()
                self.logger.info(f"Connection test successful. Found {count} emails in inbox.")
                
                return True
                
        except Exception as e:
            self.logger.error(f"Connection test failed: {e}")
            return False
        finally:
            if not self.config.email.use_gmail_api:
                self.disconnect()


# Import email.header at the top level
import email.header 