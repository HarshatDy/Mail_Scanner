"""
Gmail API connector for the Email Scanner system.
Handles Gmail API connections with OAuth2 authentication for reading and sending emails.
"""

import base64
import email
import json
import os
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import logging

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from src.config.config_manager import get_config
from src.utils.logger import get_logger


class GmailAPIConnector:
    """Gmail API connector with OAuth2 support for reading and sending emails."""
    
    # Gmail API scopes
    SCOPES = [
        'https://www.googleapis.com/auth/gmail.readonly',
        'https://www.googleapis.com/auth/gmail.send',
        'https://www.googleapis.com/auth/gmail.modify'
    ]
    
    def __init__(self):
        self.config = get_config()
        self.logger = get_logger("gmail_api_connector")
        self.service = None
        self.credentials = None
        
    def authenticate(self) -> bool:
        """Authenticate with Gmail API using OAuth2."""
        try:
            # Check if credentials file exists
            creds_file = self.config.email.credentials_file
            token_file = self.config.email.token_file
            
            if not os.path.exists(creds_file):
                self.logger.error(f"Credentials file not found: {creds_file}")
                self.logger.info("Please download credentials.json from Google Cloud Console")
                return False
            
            # Load existing credentials if available
            if os.path.exists(token_file):
                self.credentials = Credentials.from_authorized_user_file(token_file, self.SCOPES)
            
            # If credentials are invalid or don't exist, refresh or create new ones
            if not self.credentials or not self.credentials.valid:
                if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                    self.credentials.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(creds_file, self.SCOPES)
                    self.credentials = flow.run_local_server(port=6006)
                
                # Save credentials for next run
                with open(token_file, 'w') as token:
                    token.write(self.credentials.to_json())
            
            # Build the Gmail API service
            self.service = build('gmail', 'v1', credentials=self.credentials)
            
            self.logger.info("Successfully authenticated with Gmail API")
            return True
            
        except Exception as e:
            self.logger.error(f"Authentication failed: {e}")
            return False
    
    def test_connection(self) -> bool:
        """Test the Gmail API connection and authentication."""
        try:
            if not self.authenticate():
                return False
            
            # Try to get profile info as a test
            profile = self.service.users().getProfile(userId='me').execute()
            self.logger.info(f"Connection test successful. Connected as: {profile.get('emailAddress')}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Connection test failed: {e}")
            return False
    
    def fetch_emails(self, 
                    query: str = "in:inbox",
                    limit: int = 50,
                    days_back: int = 7,
                    unread_only: bool = False) -> List[Dict[str, Any]]:
        """
        Fetch emails from Gmail using the API.
        
        Args:
            query: Gmail search query (default: in:inbox)
            limit: Maximum number of emails to fetch
            days_back: Number of days back to search
            unread_only: Only fetch unread emails
            
        Returns:
            List of email dictionaries with metadata and content
        """
        emails = []
        
        try:
            if not self.service:
                if not self.authenticate():
                    return emails
            
            # Build search query
            search_query = query
            
            if unread_only:
                search_query += " is:unread"
            
            if days_back > 0:
                date_since = (datetime.now() - timedelta(days=days_back)).strftime("%Y/%m/%d")
                search_query += f" after:{date_since}"
            
            self.logger.info(f"Searching emails with query: {search_query}")
            
            # Get message IDs
            response = self.service.users().messages().list(
                userId='me',
                q=search_query,
                maxResults=limit
            ).execute()
            
            messages = response.get('messages', [])
            
            if not messages:
                self.logger.info("No emails found matching criteria")
                return emails
            
            self.logger.info(f"Found {len(messages)} emails to process")
            
            # Fetch each email
            for message in messages:
                try:
                    email_data = self._fetch_single_email(message['id'])
                    if email_data:
                        emails.append(email_data)
                except Exception as e:
                    self.logger.error(f"Error fetching email {message['id']}: {e}")
                    continue
            
            return emails
            
        except Exception as e:
            self.logger.error(f"Error fetching emails: {e}")
            return emails
    
    def _fetch_single_email(self, message_id: str) -> Optional[Dict[str, Any]]:
        """Fetch a single email by its ID."""
        try:
            # Get the full message
            message = self.service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()
            
            # Extract headers
            headers = message['payload']['headers']
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '')
            sender = next((h['value'] for h in headers if h['name'] == 'From'), '')
            recipient = next((h['value'] for h in headers if h['name'] == 'To'), '')
            date = next((h['value'] for h in headers if h['name'] == 'Date'), '')
            message_id_header = next((h['value'] for h in headers if h['name'] == 'Message-ID'), '')
            
            # Extract body
            body = self._extract_body_from_payload(message['payload'])
            
            # Extract attachments
            attachments = self._extract_attachments_from_payload(message['payload'])
            
            email_data = {
                'id': message_id,
                'thread_id': message.get('threadId', ''),
                'subject': subject,
                'from': sender,
                'to': recipient,
                'date': date,
                'message_id': message_id_header,
                'body': body,
                'headers': {h['name']: h['value'] for h in headers},
                'attachments': attachments,
                'labels': message.get('labelIds', [])
            }
            
            return email_data
            
        except Exception as e:
            self.logger.error(f"Error parsing email {message_id}: {e}")
            return None
    
    def _extract_body_from_payload(self, payload: Dict[str, Any]) -> str:
        """Extract the text body from a Gmail API payload."""
        body = ""
        
        if 'parts' in payload:
            # Multipart message
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    if 'data' in part['body']:
                        body += base64.urlsafe_b64decode(part['body']['data']).decode('utf-8', errors='ignore')
                elif part['mimeType'] == 'text/html' and not body:
                    # Use HTML if no plain text available
                    if 'data' in part['body']:
                        body += base64.urlsafe_b64decode(part['body']['data']).decode('utf-8', errors='ignore')
        else:
            # Single part message
            if payload['mimeType'] == 'text/plain':
                if 'data' in payload['body']:
                    body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8', errors='ignore')
            elif payload['mimeType'] == 'text/html':
                if 'data' in payload['body']:
                    body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8', errors='ignore')
        
        return body.strip()
    
    def _extract_attachments_from_payload(self, payload: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract attachment information from a Gmail API payload."""
        attachments = []
        
        def extract_from_parts(parts):
            for part in parts:
                if 'filename' in part and part['filename']:
                    attachments.append({
                        'filename': part['filename'],
                        'content_type': part['mimeType'],
                        'size': part['body'].get('size', 0),
                        'attachment_id': part['body'].get('attachmentId', '')
                    })
                elif 'parts' in part:
                    extract_from_parts(part['parts'])
        
        if 'parts' in payload:
            extract_from_parts(payload['parts'])
        
        return attachments
    
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
            if not self.service:
                if not self.authenticate():
                    return False
            
            # Create the email message
            message = MIMEMultipart()
            message['to'] = to
            message['subject'] = subject
            
            if cc:
                message['cc'] = cc
            
            # Add body
            if body_type == 'html':
                text_part = MIMEText(body, 'html')
            else:
                text_part = MIMEText(body, 'plain')
            
            message.attach(text_part)
            
            # Encode the message
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
            
            # Prepare the message for the API
            gmail_message = {
                'raw': raw_message
            }
            
            # Send the email
            sent_message = self.service.users().messages().send(
                userId='me',
                body=gmail_message
            ).execute()
            
            self.logger.info(f"Email sent successfully. Message ID: {sent_message['id']}")
            return True
            
        except HttpError as e:
            self.logger.error(f"Gmail API error sending email: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Error sending email: {e}")
            return False
    
    def mark_as_read(self, message_ids: List[str]) -> bool:
        """Mark emails as read using Gmail API."""
        try:
            if not self.service:
                if not self.authenticate():
                    return False
            
            # Remove UNREAD label from messages
            self.service.users().messages().batchModify(
                userId='me',
                body={
                    'ids': message_ids,
                    'removeLabelIds': ['UNREAD']
                }
            ).execute()
            
            self.logger.info(f"Marked {len(message_ids)} emails as read")
            return True
            
        except Exception as e:
            self.logger.error(f"Error marking emails as read: {e}")
            return False
    
    def add_label(self, message_ids: List[str], label_name: str) -> bool:
        """Add a label to emails using Gmail API."""
        try:
            if not self.service:
                if not self.authenticate():
                    return False
            
            # First, create the label if it doesn't exist
            label_id = self._get_or_create_label(label_name)
            
            # Add label to messages
            self.service.users().messages().batchModify(
                userId='me',
                body={
                    'ids': message_ids,
                    'addLabelIds': [label_id]
                }
            ).execute()
            
            self.logger.info(f"Added label '{label_name}' to {len(message_ids)} emails")
            return True
            
        except Exception as e:
            self.logger.error(f"Error adding label: {e}")
            return False
    
    def _get_or_create_label(self, label_name: str) -> str:
        """Get existing label ID or create a new label."""
        try:
            # Get all labels
            results = self.service.users().labels().list(userId='me').execute()
            labels = results.get('labels', [])
            
            # Look for existing label
            for label in labels:
                if label['name'] == label_name:
                    return label['id']
            
            # Create new label
            label_object = {
                'name': label_name,
                'labelListVisibility': 'labelShow',
                'messageListVisibility': 'show'
            }
            
            created_label = self.service.users().labels().create(
                userId='me',
                body=label_object
            ).execute()
            
            return created_label['id']
            
        except Exception as e:
            self.logger.error(f"Error creating label: {e}")
            return label_name
    
    def get_labels(self) -> List[Dict[str, Any]]:
        """Get list of available labels."""
        try:
            if not self.service:
                if not self.authenticate():
                    return []
            
            results = self.service.users().labels().list(userId='me').execute()
            return results.get('labels', [])
            
        except Exception as e:
            self.logger.error(f"Error getting labels: {e}")
            return []
    
    def get_email_count(self, query: str = "in:inbox") -> int:
        """Get the number of emails matching a query."""
        try:
            if not self.service:
                if not self.authenticate():
                    return 0
            
            response = self.service.users().messages().list(
                userId='me',
                q=query
            ).execute()
            
            return response.get('resultSizeEstimate', 0)
            
        except Exception as e:
            self.logger.error(f"Error getting email count: {e}")
            return 0 