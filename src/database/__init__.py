"""
Database module for the Email Scanner system.
Provides data storage and retrieval functionality.
"""

from .operations import (
    get_statistics,
    store_email,
    store_topic,
    log_scan,
    DatabaseManager
)

__all__ = [
    'get_statistics',
    'store_email', 
    'store_topic',
    'log_scan',
    'DatabaseManager'
] 