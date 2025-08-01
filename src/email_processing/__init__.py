"""
Email module for the Email Scanner system.
Provides Gmail integration, filtering, and categorization capabilities.
"""

from .connector import GmailConnector
from .filter import EmailFilter
from .categorizer import EmailCategorizer

__all__ = ['GmailConnector', 'EmailFilter', 'EmailCategorizer'] 