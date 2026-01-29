#!/usr/bin/env python3
"""
Test script for the updated email report functionality.
This script tests the enhanced email report with source email details.
"""

import os
import sys
from datetime import datetime, timedelta
from typing import List, Dict, Any
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.config.config_manager import get_config
from src.email_processing.sender import EmailSender
from src.utils.logger import get_logger

def create_sample_emails() -> List[Dict[str, Any]]:
    """Create sample email data for testing."""
    return [
        {
            'id': 'sample_1',
            'subject': 'New AI Developments in Machine Learning',
            'from': 'tech-news@example.com',
            'date': 'Mon, 03 Aug 2025 10:30:00 +0000',
            'category': 'tech',
            'relevance_score': 0.85,
            'quality_score': 0.78,
            'content': 'Latest developments in machine learning and AI...'
        },
        {
            'id': 'sample_2',
            'subject': 'Weekly Newsletter: Programming Tips',
            'from': 'newsletter@coding.com',
            'date': 'Mon, 03 Aug 2025 14:15:00 +0000',
            'category': 'newsletter',
            'relevance_score': 0.72,
            'quality_score': 0.65,
            'content': 'This week\'s programming tips and tricks...'
        },
        {
            'id': 'sample_3',
            'subject': 'Professional Development: Leadership Skills',
            'from': 'hr@company.com',
            'date': 'Mon, 03 Aug 2025 16:45:00 +0000',
            'category': 'professional',
            'relevance_score': 0.68,
            'quality_score': 0.71,
            'content': 'Important leadership skills for managers...'
        }
    ]

def create_sample_topics() -> List[Dict[str, Any]]:
    """Create sample topics with source email information."""
    sample_emails = create_sample_emails()
    
    return [
        {
            'title': 'Building Scalable Machine Learning Systems',
            'description': 'A comprehensive guide to designing and implementing scalable ML systems for production environments.',
            'keywords': ['machine learning', 'scalability', 'production', 'AI systems'],
            'difficulty': 'Advanced',
            'category': 'tech',
            'source_emails': [
                {
                    'subject': email['subject'],
                    'from': email['from'],
                    'date': email['date'],
                    'category': email['category'],
                    'relevance_score': email['relevance_score'],
                    'quality_score': email['quality_score']
                }
                for email in sample_emails if email['category'] == 'tech'
            ]
        },
        {
            'title': 'Effective Code Review Practices',
            'description': 'Best practices for conducting thorough and constructive code reviews in development teams.',
            'keywords': ['code review', 'development', 'team collaboration', 'best practices'],
            'difficulty': 'Intermediate',
            'category': 'newsletter',
            'source_emails': [
                {
                    'subject': email['subject'],
                    'from': email['from'],
                    'date': email['date'],
                    'category': email['category'],
                    'relevance_score': email['relevance_score'],
                    'quality_score': email['quality_score']
                }
                for email in sample_emails if email['category'] == 'newsletter'
            ]
        }
    ]

def test_updated_email_report():
    """Test the updated email report functionality."""
    logger = get_logger("test_email_report")
    
    try:
        # Get configuration
        config = get_config()
        
        # Check if notification email is configured
        if not config.notifications.notification_email:
            logger.error("❌ No notification email configured. Please set NOTIFICATION_EMAIL environment variable.")
            return False
        
        # Initialize email sender
        email_sender = EmailSender()
        
        # Create sample data
        sample_emails = create_sample_emails()
        sample_topics = create_sample_topics()
        
        logger.info(f"📧 Testing email report with {len(sample_topics)} topics and {len(sample_emails)} source emails")
        
        # Test email sending
        success = email_sender.send_email(
            to=config.notifications.notification_email,
            subject=f"🧪 Test: Updated Email Report - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            body="This is a test of the updated email report functionality.",
            body_type='plain'
        )
        
        if success:
            logger.info("✅ Basic email sending test passed")
        else:
            logger.error("❌ Basic email sending test failed")
            return False
        
        # Test the full topics email functionality
        from src.scheduler.jobs import send_topics_email
        
        success = send_topics_email(
            email_sender=email_sender,
            topics=sample_topics,
            recipient=config.notifications.notification_email,
            source_emails=sample_emails
        )
        
        if success:
            logger.info("✅ Updated email report test passed")
            logger.info("📧 Email sent successfully with source email details")
            return True
        else:
            logger.error("❌ Updated email report test failed")
            return False
            
    except Exception as e:
        logger.error(f"❌ Test failed with error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Updated Email Report Functionality")
    print("=" * 50)
    
    success = test_updated_email_report()
    
    if success:
        print("\n✅ All tests passed! The updated email report is working correctly.")
        print("📧 Check your email for the test report with source email details.")
    else:
        print("\n❌ Tests failed. Please check the configuration and try again.")
        print("💡 Make sure to set the NOTIFICATION_EMAIL environment variable.") 