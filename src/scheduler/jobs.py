"""
Scheduler jobs for the Email Scanner system.
Handles email scanning and processing tasks.
"""

import time
import random
from typing import Dict, List, Any, Optional
from datetime import datetime

from src.email_processing.connector import GmailConnector
from src.email_processing.filter import EmailFilter
from src.email_processing.categorizer import EmailCategorizer
from src.email_processing.sender import EmailSender
from src.ai.topic_generator import TopicGenerator
from src.ai.content_analyzer import ContentAnalyzer
from src.config.config_manager import get_config
from src.utils.logger import get_logger


def run_email_scan() -> bool:
    """
    Run a complete email scan and processing job.
    Scans up to 50 emails from random dates, filters by priority senders,
    randomly selects 3 emails, and generates blog content.
    
    Returns:
        bool: True if scan completed successfully, False otherwise
    """
    logger = get_logger("email_scan")
    config = get_config()
    
    try:
        logger.info("Starting email scan for Software Engineering blog content...")
        
        # Initialize components
        connector = GmailConnector()
        filter_engine = EmailFilter()
        content_analyzer = ContentAnalyzer()
        topic_generator = TopicGenerator()
        email_sender = EmailSender()
        
        # Connect to Gmail
        if not connector.connect():
            logger.error("Failed to connect to Gmail")
            return False
        
        try:
            # Fetch up to 50 emails from random dates (use wider date range)
            logger.info("Fetching up to 50 emails from random dates...")
            emails = connector.fetch_emails(
                folder="INBOX",
                limit=50,
                days_back=30,  # Look back 30 days for more variety
                unread_only=False,
                random_dates=True
            )
            
            if not emails:
                logger.info("No emails found to process")
                return True
            
            logger.info(f"Found {len(emails)} emails to process")
            
            # Filter emails by priority senders (Software Engineering newsletters)
            priority_emails = filter_engine.filter_by_priority_senders(emails)
            
            if not priority_emails:
                logger.info("No emails found from priority senders")
                # Fall back to filtering by Software Engineering keywords
                categorized_emails = filter_engine.filter_emails(emails)
                priority_emails = []
                for category, email_list in categorized_emails.items():
                    if category == 'tech':
                        for email_result in email_list:
                            email_data = email_result['email_data']
                            analysis = content_analyzer.analyze_email_content(email_data)
                            if content_analyzer.should_process_for_topics(email_data, analysis):
                                priority_emails.append(email_data)
            
            logger.info(f"Found {len(priority_emails)} emails from priority senders or matching Software Engineering criteria")
            
            if len(priority_emails) == 0:
                logger.info("No suitable emails found for blog generation")
                return True
            
            # Randomly select 3 emails
            num_to_select = min(3, len(priority_emails))
            selected_emails = random.sample(priority_emails, num_to_select)
            
            logger.info(f"Randomly selected {len(selected_emails)} emails for blog generation")
            
            # Generate blog content for each selected email
            blog_posts = []
            for i, email_data in enumerate(selected_emails, 1):
                logger.info(f"Generating blog content for email {i}/{len(selected_emails)}: {email_data.get('subject', 'No subject')}")
                
                try:
                    blog_content = topic_generator.generate_blog_content(email_data)
                    if blog_content and not blog_content.get('error'):
                        blog_posts.append(blog_content)
                        logger.info(f"Successfully generated blog: {blog_content.get('title', 'Untitled')}")
                    else:
                        logger.warning(f"Failed to generate blog content for email: {email_data.get('subject', 'No subject')}")
                except Exception as e:
                    logger.error(f"Error generating blog content: {e}")
                    continue
            
            if blog_posts:
                logger.info(f"Generated {len(blog_posts)} blog posts")
                
                # Send email with blog posts
                if config.notifications.email_notifications and config.notifications.notification_email:
                    success = send_blog_posts_email(
                        email_sender, 
                        blog_posts, 
                        config.notifications.notification_email,
                        selected_emails
                    )
                    if success:
                        logger.info("Blog posts email sent successfully")
                    else:
                        logger.error("Failed to send blog posts email")
                else:
                    logger.warning("Email notifications not configured")
            else:
                logger.info("No blog posts generated")
            
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


def send_blog_posts_email(email_sender: EmailSender, blog_posts: List[Dict[str, Any]], recipient: str, source_emails: List[Dict[str, Any]] = None) -> bool:
    """
    Send an email with generated blog posts (titles and content).
    
    Args:
        email_sender: Email sender instance
        blog_posts: List of generated blog posts with title and content
        recipient: Email address to send to
        source_emails: List of source emails used for blog generation
        
    Returns:
        True if email sent successfully, False otherwise
    """
    try:
        subject = f"📝 Software Engineering Blog Posts - {datetime.now().strftime('%Y-%m-%d')}"
        
        # Format blog posts as HTML
        html_body = format_blog_posts_as_html(blog_posts, source_emails)
        
        return email_sender.send_email(
            to=recipient,
            subject=subject,
            body=html_body,
            body_type='html'
        )
        
    except Exception as e:
        logger = get_logger("blog_email")
        logger.error(f"Error sending blog posts email: {e}")
        return False


def format_blog_posts_as_html(blog_posts: List[Dict[str, Any]], source_emails: List[Dict[str, Any]] = None) -> str:
    """Format blog posts as HTML for email."""
    try:
        html_parts = [
            """
            <html>
            <body style="font-family: Arial, sans-serif; max-width: 900px; margin: 0 auto; padding: 20px; background-color: #f5f5f5;">
                <div style="background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <h1 style="color: #1976d2; border-bottom: 3px solid #1976d2; padding-bottom: 15px; margin-bottom: 30px;">
                        🚀 Software Engineering Blog Posts
                    </h1>
                    <p style="color: #666; font-size: 14px; margin-bottom: 30px;">
                        Generated on: """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """
                    </p>
            """
        ]
        
        # Add each blog post
        for i, blog_post in enumerate(blog_posts, 1):
            title = blog_post.get('title', 'Untitled Blog Post')
            content = blog_post.get('content', 'No content available')
            source_email = blog_post.get('source_email', 'Unknown')
            source_subject = blog_post.get('source_subject', 'No subject')
            
            # Format content with basic HTML (preserve line breaks)
            # Split by double newlines for paragraphs
            paragraphs = content.split('\n\n')
            formatted_paragraphs = []
            for para in paragraphs:
                if para.strip():
                    # Replace single newlines with <br> within paragraphs
                    para = para.replace('\n', '<br>')
                    formatted_paragraphs.append(f'<p style="margin: 10px 0; line-height: 1.6; color: #333;">{para}</p>')
            
            formatted_content = '\n'.join(formatted_paragraphs) if formatted_paragraphs else f'<p style="margin: 10px 0; line-height: 1.6; color: #333;">{content.replace(chr(10), "<br>")}</p>'
            
            html_parts.append(f"""
                <div style="background-color: #f8f9fa; border-left: 5px solid #1976d2; 
                           padding: 25px; margin: 30px 0; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                    <h2 style="color: #1976d2; margin-top: 0; font-size: 24px; line-height: 1.3;">
                        Blog Post {i}: {title}
                    </h2>
                    <div style="background-color: white; padding: 20px; border-radius: 6px; margin: 15px 0;">
                        {formatted_content}
                    </div>
                    <div style="margin-top: 20px; padding-top: 15px; border-top: 1px solid #ddd;">
                        <p style="color: #666; font-size: 12px; margin: 5px 0;">
                            <strong>📧 Source Email:</strong> {source_email}
                        </p>
                        <p style="color: #666; font-size: 12px; margin: 5px 0;">
                            <strong>📌 Original Subject:</strong> {source_subject}
                        </p>
                    </div>
                </div>
            """)
        
        # Add source email details section
        if source_emails:
            html_parts.append("""
                <hr style="margin: 40px 0; border: none; border-top: 2px solid #ddd;">
                <h2 style="color: #333; border-bottom: 2px solid #1976d2; padding-bottom: 10px;">
                    📧 Source Emails Used
                </h2>
                <p style="color: #666; font-size: 14px; margin-bottom: 20px;">
                    The following emails were used to generate these blog posts:
                </p>
            """)
            
            for i, email in enumerate(source_emails, 1):
                email_date = email.get('date', '')
                try:
                    from email.utils import parsedate_to_datetime
                    parsed_date = parsedate_to_datetime(email_date)
                    formatted_date = parsed_date.strftime('%Y-%m-%d %H:%M:%S')
                except:
                    formatted_date = email_date
                
                sender = email.get('from', 'Unknown')
                subject = email.get('subject', 'No Subject')
                
                html_parts.append(f"""
                    <div style="background-color: #f8f9fa; border-left: 4px solid #4caf50; 
                               padding: 15px; margin: 10px 0; border-radius: 6px;">
                        <h3 style="color: #333; margin: 0 0 8px 0; font-size: 16px;">
                            {i}. {subject}
                        </h3>
                        <p style="color: #666; margin: 5px 0; font-size: 14px;">
                            <strong>From:</strong> {sender}
                        </p>
                        <p style="color: #666; margin: 5px 0; font-size: 14px;">
                            <strong>Received:</strong> {formatted_date}
                        </p>
                    </div>
                """)
        
        html_parts.append("""
                </div>
                <hr style="margin: 30px 0; border: none; border-top: 1px solid #ddd;">
                <p style="color: #999; font-size: 12px; text-align: center;">
                    Generated by Email Scanner & Blog Content Generator
                </p>
            </body>
            </html>
        """)
        
        return "\n".join(html_parts)
        
    except Exception as e:
        logger = get_logger("blog_formatting")
        logger.error(f"Error formatting blog posts as HTML: {e}")
        return f"<p>Error formatting blog posts: {e}</p>"


def send_topics_email(email_sender: EmailSender, topics: List[Dict[str, Any]], recipient: str, source_emails: List[Dict[str, Any]] = None) -> bool:
    """
    Send an email with generated topics and source email details.
    
    Args:
        email_sender: Email sender instance
        topics: List of generated topics
        recipient: Email address to send to
        source_emails: List of source emails used for topic generation
        
    Returns:
        True if email sent successfully, False otherwise
    """
    try:
        subject = f"📝 Blog Topics Generated - {datetime.now().strftime('%Y-%m-%d')}"
        
        # Format topics as HTML with source email details
        html_body = format_topics_as_html(topics, source_emails)
        
        return email_sender.send_email(
            to=recipient,
            subject=subject,
            body=html_body,
            body_type='html'
        )
        
    except Exception as e:
        logger = get_logger("topic_email")
        logger.error(f"Error sending topics email: {e}")
        return False


def format_topics_as_html(topics: List[Dict[str, Any]], source_emails: List[Dict[str, Any]] = None) -> str:
    """Format topics as HTML for email with source email details."""
    try:
        html_parts = [
            """
            <html>
            <body style="font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px;">
                <h1 style="color: #1976d2; border-bottom: 2px solid #1976d2; padding-bottom: 10px;">
                    🚀 Blog Topics Generated
                </h1>
                <p style="color: #666; font-size: 14px;">
                    Generated on: """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """
                </p>
            """
        ]
        
        # Add summary statistics
        if source_emails:
            total_emails = len(source_emails)
            categories = {}
            for email in source_emails:
                category = email.get('category', 'unknown')
                categories[category] = categories.get(category, 0) + 1
            
            html_parts.append(f"""
                <div style="background-color: #e3f2fd; border: 1px solid #2196f3; 
                           padding: 15px; margin: 20px 0; border-radius: 8px;">
                    <h3 style="color: #1976d2; margin: 0 0 10px 0;">📊 Analysis Summary</h3>
                    <div style="display: flex; justify-content: space-between; flex-wrap: wrap;">
                        <div style="flex: 1; min-width: 200px;">
                            <p style="margin: 5px 0; color: #333;">
                                <strong>Total Emails Analyzed:</strong> {total_emails}
                            </p>
                            <p style="margin: 5px 0; color: #333;">
                                <strong>Topics Generated:</strong> {len(topics)}
                            </p>
                        </div>
                        <div style="flex: 1; min-width: 200px;">
                            <p style="margin: 5px 0; color: #333;">
                                <strong>Categories Found:</strong>
                            </p>
                            <div style="margin-left: 10px;">
            """)
            
            for category, count in categories.items():
                category_color = {
                    'tech': '#2196f3',
                    'newsletter': '#9c27b0',
                    'professional': '#ff5722'
                }.get(category, '#666')
                
                html_parts.append(f"""
                                    <p style="margin: 2px 0; color: #666; font-size: 14px;">
                                        <span style="background-color: {category_color}; color: white; 
                                                   padding: 2px 6px; border-radius: 3px; font-size: 12px;">
                                            {category.title()}
                                        </span>
                                        <span style="margin-left: 8px;">{count} emails</span>
                                    </p>
                """)
            
            html_parts.append("""
                            </div>
                        </div>
                    </div>
                </div>
            """)
        
        for i, topic in enumerate(topics, 1):
            title = topic.get('title', 'Untitled')
            description = topic.get('description', 'No description available')
            keywords = topic.get('keywords', [])
            difficulty = topic.get('difficulty', 'Intermediate')
            category = topic.get('category', 'General')
            
            # Color coding for difficulty
            difficulty_color = {
                'Beginner': '#4caf50',
                'Intermediate': '#ff9800',
                'Advanced': '#f44336'
            }.get(difficulty, '#666')
            
            # Color coding for category
            category_color = {
                'tech': '#2196f3',
                'newsletter': '#9c27b0',
                'professional': '#ff5722'
            }.get(category, '#666')
            
            # Add source email information for this topic
            source_emails_info = ""
            if topic.get('source_emails'):
                source_emails_info = """
                    <div style="margin-top: 15px; padding-top: 15px; border-top: 1px solid #ddd;">
                        <p style="color: #666; font-size: 12px; margin-bottom: 8px;">
                            <strong>📧 Based on emails from:</strong>
                        </p>
                """
                
                for source_email in topic['source_emails'][:3]:  # Show first 3 emails
                    try:
                        from email.utils import parsedate_to_datetime
                        parsed_date = parsedate_to_datetime(source_email.get('date', ''))
                        formatted_date = parsed_date.strftime('%Y-%m-%d %H:%M')
                    except:
                        formatted_date = source_email.get('date', '')
                    
                    source_emails_info += f"""
                        <div style="background-color: #f0f0f0; padding: 8px; margin: 5px 0; border-radius: 4px;">
                            <p style="margin: 2px 0; font-size: 12px; color: #333;">
                                <strong>{source_email.get('subject', 'No Subject')}</strong>
                            </p>
                            <p style="margin: 2px 0; font-size: 11px; color: #666;">
                                From: {source_email.get('from', 'Unknown')} | 
                                Received: {formatted_date} | 
                                Score: {source_email.get('relevance_score', 0.0):.2f}
                            </p>
                        </div>
                    """
                
                if len(topic['source_emails']) > 3:
                    source_emails_info += f"""
                        <p style="color: #999; font-size: 11px; margin-top: 5px;">
                            + {len(topic['source_emails']) - 3} more emails
                        </p>
                    """
                
                source_emails_info += "</div>"
            
            html_parts.append(f"""
                <div style="background-color: #f8f9fa; border-left: 4px solid {category_color}; 
                           padding: 20px; margin: 20px 0; border-radius: 8px;">
                    <h2 style="color: #333; margin-top: 0;">
                        {i}. {title}
                    </h2>
                    <p style="color: #666; line-height: 1.6;">
                        {description}
                    </p>
                    <div style="margin-top: 15px;">
                        <span style="background-color: {difficulty_color}; color: white; 
                                   padding: 4px 8px; border-radius: 4px; font-size: 12px;">
                            {difficulty}
                        </span>
                        <span style="background-color: {category_color}; color: white; 
                                   padding: 4px 8px; border-radius: 4px; font-size: 12px; margin-left: 8px;">
                            {category.title()}
                        </span>
                    </div>
                    <div style="margin-top: 10px;">
                        <strong>Keywords:</strong>
                        <span style="color: #666; font-size: 14px;">
                            {', '.join(keywords)}
                        </span>
                    </div>
                    {source_emails_info}
                </div>
            """)
        
        # Add source email details section
        if source_emails:
            html_parts.append("""
                <hr style="margin: 30px 0; border: none; border-top: 1px solid #ddd;">
                <h2 style="color: #333; border-bottom: 1px solid #ddd; padding-bottom: 10px;">
                    📧 Source Emails Used
                </h2>
                <p style="color: #666; font-size: 14px; margin-bottom: 20px;">
                    The following emails were analyzed to generate these topics:
                </p>
            """)
            
            for i, email in enumerate(source_emails, 1):
                # Parse email date
                email_date = email.get('date', '')
                try:
                    # Try to parse the date string
                    from email.utils import parsedate_to_datetime
                    parsed_date = parsedate_to_datetime(email_date)
                    formatted_date = parsed_date.strftime('%Y-%m-%d %H:%M:%S')
                except:
                    formatted_date = email_date
                
                sender = email.get('from', 'Unknown')
                subject = email.get('subject', 'No Subject')
                category = email.get('category', 'Unknown')
                relevance_score = email.get('relevance_score', 0.0)
                quality_score = email.get('quality_score', 0.0)
                
                # Color coding for category
                category_color = {
                    'tech': '#2196f3',
                    'newsletter': '#9c27b0',
                    'professional': '#ff5722'
                }.get(category, '#666')
                
                html_parts.append(f"""
                    <div style="background-color: #f8f9fa; border-left: 4px solid {category_color}; 
                               padding: 15px; margin: 10px 0; border-radius: 6px;">
                        <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                            <div style="flex: 1;">
                                <h3 style="color: #333; margin: 0 0 8px 0; font-size: 16px;">
                                    {i}. {subject}
                                </h3>
                                <p style="color: #666; margin: 5px 0; font-size: 14px;">
                                    <strong>From:</strong> {sender}
                                </p>
                                <p style="color: #666; margin: 5px 0; font-size: 14px;">
                                    <strong>Received:</strong> {formatted_date}
                                </p>
                                <p style="color: #666; margin: 5px 0; font-size: 14px;">
                                    <strong>Category:</strong> 
                                    <span style="background-color: {category_color}; color: white; 
                                               padding: 2px 6px; border-radius: 3px; font-size: 12px;">
                                        {category.title()}
                                    </span>
                                </p>
                            </div>
                            <div style="text-align: right; margin-left: 15px;">
                                <p style="color: #666; margin: 2px 0; font-size: 12px;">
                                    <strong>Relevance:</strong> {relevance_score:.2f}
                                </p>
                                <p style="color: #666; margin: 2px 0; font-size: 12px;">
                                    <strong>Quality:</strong> {quality_score:.2f}
                                </p>
                            </div>
                        </div>
                    </div>
                """)
        
        html_parts.append("""
                <hr style="margin: 30px 0; border: none; border-top: 1px solid #ddd;">
                <p style="color: #999; font-size: 12px; text-align: center;">
                    Generated by Email Scanner & Blog Topic Generator
                </p>
            </body>
            </html>
        """)
        
        return "\n".join(html_parts)
        
    except Exception as e:
        logger = get_logger("topic_formatting")
        logger.error(f"Error formatting topics as HTML: {e}")
        return f"<p>Error formatting topics: {e}</p>" 