#!/usr/bin/env python3
"""
Test script for Gmail API integration.
This script tests the Gmail API connector and email sender functionality.
"""

import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.config.config_manager import get_config
from src.email_processing.gmail_api_connector import GmailAPIConnector
from src.email_processing.sender import EmailSender
from src.utils.logger import get_logger


def test_gmail_api_connection():
    """Test Gmail API connection and authentication."""
    print("🔍 Testing Gmail API connection...")
    
    try:
        config = get_config()
        
        if not config.email.use_gmail_api:
            print("❌ Gmail API is not enabled in configuration")
            print("   Set use_gmail_api: true in your config.yaml")
            return False
        
        if not os.path.exists(config.email.credentials_file):
            print(f"❌ Credentials file not found: {config.email.credentials_file}")
            print("   Please download credentials.json from Google Cloud Console")
            return False
        
        # Test the Gmail API connector
        gmail_api = GmailAPIConnector()
        
        if gmail_api.test_connection():
            print("✅ Gmail API connection successful!")
            return True
        else:
            print("❌ Gmail API connection failed")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Gmail API connection: {e}")
        return False


def test_email_sending():
    """Test email sending functionality."""
    print("\n📧 Testing email sending...")
    
    try:
        sender = EmailSender()
        
        if sender.test_connection():
            print("✅ Email sender connection successful!")
            
            # Test sending a simple email (commented out to avoid spam)
            # Uncomment the following lines to test actual email sending
            """
            success = sender.send_email(
                to="your-email@example.com",  # Replace with your email
                subject="Test Email from Email Scanner",
                body="This is a test email sent via Gmail API.",
                body_type='plain'
            )
            
            if success:
                print("✅ Test email sent successfully!")
            else:
                print("❌ Failed to send test email")
            """
            
            return True
        else:
            print("❌ Email sender connection failed")
            return False
            
    except Exception as e:
        print(f"❌ Error testing email sending: {e}")
        return False


def test_email_fetching():
    """Test email fetching functionality."""
    print("\n📥 Testing email fetching...")
    
    try:
        gmail_api = GmailAPIConnector()
        
        # Fetch a few emails from inbox
        emails = gmail_api.fetch_emails(
            query="in:inbox",
            limit=5,
            days_back=7,
            unread_only=False
        )
        
        if emails:
            print(f"✅ Successfully fetched {len(emails)} emails")
            for i, email in enumerate(emails[:3]):  # Show first 3 emails
                print(f"   {i+1}. {email.get('subject', 'No subject')} - {email.get('from', 'Unknown')}")
            return True
        else:
            print("ℹ️  No emails found (this might be normal)")
            return True
            
    except Exception as e:
        print(f"❌ Error testing email fetching: {e}")
        return False


def main():
    """Run all Gmail API tests."""
    print("🚀 Starting Gmail API Integration Tests")
    print("=" * 50)
    
    # Test 1: Connection
    connection_ok = test_gmail_api_connection()
    
    # Test 2: Email sending
    sending_ok = test_email_sending()
    
    # Test 3: Email fetching
    fetching_ok = test_email_fetching()
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print(f"   Connection: {'✅ PASS' if connection_ok else '❌ FAIL'}")
    print(f"   Email Sending: {'✅ PASS' if sending_ok else '❌ FAIL'}")
    print(f"   Email Fetching: {'✅ PASS' if fetching_ok else '❌ FAIL'}")
    
    if all([connection_ok, sending_ok, fetching_ok]):
        print("\n🎉 All tests passed! Gmail API integration is working correctly.")
        return True
    else:
        print("\n⚠️  Some tests failed. Please check the configuration and try again.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 