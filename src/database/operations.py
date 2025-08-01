"""
Database operations for the Email Scanner system.
Provides data storage and retrieval functionality.
"""

import os
import sqlite3
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path

from src.config.config_manager import get_config
from src.utils.logger import get_logger


class DatabaseManager:
    """Manages database operations for the email scanner."""
    
    def __init__(self):
        self.config = get_config()
        self.logger = get_logger("database")
        self.db_path = self._get_db_path()
        self._ensure_db_directory()
        self._init_database()
    
    def _get_db_path(self) -> str:
        """Get the database file path."""
        db_url = self.config.database.url
        if db_url.startswith('sqlite:///'):
            return db_url.replace('sqlite:///', '')
        return 'data/emails.db'
    
    def _ensure_db_directory(self):
        """Ensure the database directory exists."""
        db_dir = os.path.dirname(self.db_path)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)
    
    def _init_database(self):
        """Initialize the database with required tables."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create emails table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS emails (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        uid TEXT UNIQUE,
                        subject TEXT,
                        sender TEXT,
                        recipient TEXT,
                        date TEXT,
                        category TEXT,
                        confidence REAL,
                        content_hash TEXT,
                        processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        body TEXT,
                        metadata TEXT
                    )
                ''')
                
                # Create topics table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS topics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT,
                        description TEXT,
                        keywords TEXT,
                        category TEXT,
                        source_emails TEXT,
                        generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        status TEXT DEFAULT 'pending'
                    )
                ''')
                
                # Create scan_logs table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS scan_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        scan_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        emails_processed INTEGER,
                        emails_categorized INTEGER,
                        topics_generated INTEGER,
                        status TEXT,
                        duration REAL,
                        error_message TEXT
                    )
                ''')
                
                conn.commit()
                self.logger.info("Database initialized successfully")
                
        except Exception as e:
            self.logger.error(f"Error initializing database: {e}")
            raise
    
    def store_email(self, email_data: Dict[str, Any], category: str, confidence: float) -> bool:
        """Store an email in the database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT OR REPLACE INTO emails 
                    (uid, subject, sender, recipient, date, category, confidence, body, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    email_data.get('uid'),
                    email_data.get('subject'),
                    email_data.get('from'),
                    email_data.get('to'),
                    email_data.get('date'),
                    category,
                    confidence,
                    email_data.get('body'),
                    str(email_data.get('headers', {}))
                ))
                
                conn.commit()
                return True
                
        except Exception as e:
            self.logger.error(f"Error storing email: {e}")
            return False
    
    def store_topic(self, topic_data: Dict[str, Any]) -> bool:
        """Store a generated topic in the database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO topics 
                    (title, description, keywords, category, source_emails, status)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    topic_data.get('title'),
                    topic_data.get('description'),
                    ','.join(topic_data.get('keywords', [])),
                    topic_data.get('category'),
                    ','.join(topic_data.get('source_emails', [])),
                    topic_data.get('status', 'pending')
                ))
                
                conn.commit()
                return True
                
        except Exception as e:
            self.logger.error(f"Error storing topic: {e}")
            return False
    
    def log_scan(self, scan_data: Dict[str, Any]) -> bool:
        """Log a scan operation."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO scan_logs 
                    (emails_processed, emails_categorized, topics_generated, status, duration, error_message)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    scan_data.get('emails_processed', 0),
                    scan_data.get('emails_categorized', 0),
                    scan_data.get('topics_generated', 0),
                    scan_data.get('status', 'unknown'),
                    scan_data.get('duration', 0),
                    scan_data.get('error_message')
                ))
                
                conn.commit()
                return True
                
        except Exception as e:
            self.logger.error(f"Error logging scan: {e}")
            return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get system statistics."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get email statistics
                cursor.execute('SELECT COUNT(*) FROM emails')
                total_emails = cursor.fetchone()[0]
                
                cursor.execute('SELECT COUNT(*) FROM emails WHERE category != "excluded"')
                categorized_emails = cursor.fetchone()[0]
                
                # Get topic statistics
                cursor.execute('SELECT COUNT(*) FROM topics')
                topics_generated = cursor.fetchone()[0]
                
                # Get last scan
                cursor.execute('''
                    SELECT scan_time, status FROM scan_logs 
                    ORDER BY scan_time DESC LIMIT 1
                ''')
                last_scan_result = cursor.fetchone()
                last_scan = last_scan_result[0] if last_scan_result else 'Never'
                
                # Get database size
                db_size = self._get_db_size()
                
                return {
                    'total_emails': total_emails,
                    'categorized_emails': categorized_emails,
                    'topics_generated': topics_generated,
                    'last_scan': last_scan,
                    'db_size': db_size
                }
                
        except Exception as e:
            self.logger.error(f"Error getting statistics: {e}")
            return {
                'total_emails': 0,
                'categorized_emails': 0,
                'topics_generated': 0,
                'last_scan': 'Error',
                'db_size': 'Unknown'
            }
    
    def _get_db_size(self) -> str:
        """Get the database file size."""
        try:
            if os.path.exists(self.db_path):
                size_bytes = os.path.getsize(self.db_path)
                if size_bytes < 1024:
                    return f"{size_bytes} B"
                elif size_bytes < 1024 * 1024:
                    return f"{size_bytes / 1024:.1f} KB"
                else:
                    return f"{size_bytes / (1024 * 1024):.1f} MB"
            return "0 B"
        except Exception:
            return "Unknown"
    
    def get_recent_emails(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent emails from the database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT uid, subject, sender, category, confidence, processed_at
                    FROM emails 
                    ORDER BY processed_at DESC 
                    LIMIT ?
                ''', (limit,))
                
                rows = cursor.fetchall()
                return [
                    {
                        'uid': row[0],
                        'subject': row[1],
                        'sender': row[2],
                        'category': row[3],
                        'confidence': row[4],
                        'processed_at': row[5]
                    }
                    for row in rows
                ]
                
        except Exception as e:
            self.logger.error(f"Error getting recent emails: {e}")
            return []
    
    def get_recent_topics(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent topics from the database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT title, description, category, status, generated_at
                    FROM topics 
                    ORDER BY generated_at DESC 
                    LIMIT ?
                ''', (limit,))
                
                rows = cursor.fetchall()
                return [
                    {
                        'title': row[0],
                        'description': row[1],
                        'category': row[2],
                        'status': row[3],
                        'generated_at': row[4]
                    }
                    for row in rows
                ]
                
        except Exception as e:
            self.logger.error(f"Error getting recent topics: {e}")
            return []


# Global database manager instance
db_manager = DatabaseManager()


def get_statistics() -> Dict[str, Any]:
    """Get system statistics."""
    return db_manager.get_statistics()


def store_email(email_data: Dict[str, Any], category: str, confidence: float) -> bool:
    """Store an email in the database."""
    return db_manager.store_email(email_data, category, confidence)


def store_topic(topic_data: Dict[str, Any]) -> bool:
    """Store a generated topic in the database."""
    return db_manager.store_topic(topic_data)


def log_scan(scan_data: Dict[str, Any]) -> bool:
    """Log a scan operation."""
    return db_manager.log_scan(scan_data) 