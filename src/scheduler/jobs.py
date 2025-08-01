"""
Scheduler jobs for the Email Scanner system.
Handles email scanning and processing tasks.
"""

import time
from typing import Dict, List, Any, Optional
from datetime import datetime

from src.email_processing.connector import GmailConnector
from src.email_processing.filter import EmailFilter
from src.email_processing.categorizer import EmailCategorizer
from src.config.config_manager import get_config
from src.utils.logger import get_logger


def run_email_scan() -> bool:
    """
    Run a complete email scan and processing job.
    
    Returns:
        bool: True if scan completed successfully, False otherwise
    """
    logger = get_logger("email_scan")
    config = get_config()
    
    try:
        logger.info("Starting email scan...")
        
        # Initialize components
        connector = GmailConnector()
        filter_engine = EmailFilter()
        categorizer = EmailCategorizer()
        
        # Connect to Gmail
        if not connector.connect():
            logger.error("Failed to connect to Gmail")
            return False
        
        try:
            # Fetch emails
            emails = connector.fetch_emails(
                folder="INBOX",
                limit=config.email.max_emails_per_scan,
                days_back=config.email.days_back,
                unread_only=config.email.scan_unread_only
            )
            
            if not emails:
                logger.info("No emails found to process")
                return True
            
            logger.info(f"Found {len(emails)} emails to process")
            
            # Filter and categorize emails
            categorized_emails = filter_engine.filter_emails(emails)
            
            # Get statistics
            stats = filter_engine.get_category_statistics(categorized_emails)
            logger.info(f"Email categorization complete: {stats}")
            
            # Process emails for topic generation
            processed_emails = []
            for category, email_list in categorized_emails.items():
                if category in ['tech', 'newsletter', 'professional']:
                    for email_result in email_list:
                        email_data = email_result['email_data']
                        
                        # Analyze email content
                        analysis = categorizer.analyze_email_content(email_data)
                        
                        # Check if email should be processed for topics
                        if categorizer.should_process_for_topics(email_data, analysis):
                            report = categorizer.create_email_report(email_data, analysis)
                            processed_emails.append(report)
                            
                            logger.info(f"Email ready for topic generation: {report['summary']}")
            
            logger.info(f"Processed {len(processed_emails)} emails for topic generation")
            
            # TODO: Generate topics using AI (implement in ai module)
            if processed_emails:
                logger.info("Emails ready for AI topic generation")
                # generate_topics(processed_emails)
            
            return True
            
        finally:
            connector.disconnect()
            
    except Exception as e:
        logger.error(f"Error during email scan: {e}")
        return False


def run_scheduled_scan() -> bool:
    """
    Run a scheduled email scan with additional logging.
    
    Returns:
        bool: True if scan completed successfully, False otherwise
    """
    logger = get_logger("scheduled_scan")
    
    logger.info("=" * 50)
    logger.info(f"Scheduled email scan started at {datetime.now()}")
    logger.info("=" * 50)
    
    start_time = time.time()
    success = run_email_scan()
    end_time = time.time()
    
    duration = end_time - start_time
    logger.info(f"Email scan completed in {duration:.2f} seconds")
    logger.info(f"Scan result: {'SUCCESS' if success else 'FAILED'}")
    logger.info("=" * 50)
    
    return success


def test_gmail_connection() -> bool:
    """
    Test Gmail connection and basic functionality.
    
    Returns:
        bool: True if connection test successful, False otherwise
    """
    logger = get_logger("connection_test")
    
    try:
        logger.info("Testing Gmail connection...")
        
        connector = GmailConnector()
        if connector.test_connection():
            logger.info("✅ Gmail connection test successful")
            return True
        else:
            logger.error("❌ Gmail connection test failed")
            return False
            
    except Exception as e:
        logger.error(f"Connection test error: {e}")
        return False


def get_scan_statistics() -> Dict[str, Any]:
    """
    Get statistics about the last scan and system status.
    
    Returns:
        Dict containing scan statistics
    """
    logger = get_logger("statistics")
    
    try:
        connector = GmailConnector()
        if not connector.connect():
            return {"error": "Failed to connect to Gmail"}
        
        try:
            # Get basic email counts
            inbox_count = connector.get_email_count("INBOX")
            
            stats = {
                "last_scan": datetime.now().isoformat(),
                "inbox_email_count": inbox_count,
                "connection_status": "connected",
                "scan_status": "ready"
            }
            
            return stats
            
        finally:
            connector.disconnect()
            
    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        return {
            "error": str(e),
            "last_scan": datetime.now().isoformat(),
            "connection_status": "error"
        } 