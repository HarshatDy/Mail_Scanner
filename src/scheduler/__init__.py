"""
Scheduler module for the Email Scanner system.
Provides automated email scanning and job management.
"""

from src.scheduler.main import start_scheduler, run_immediate_scan, get_scheduler_status
from src.scheduler.jobs import run_email_scan, run_scheduled_scan, test_gmail_connection, get_scan_statistics

__all__ = [
    'start_scheduler',
    'run_immediate_scan', 
    'get_scheduler_status',
    'run_email_scan',
    'run_scheduled_scan',
    'test_gmail_connection',
    'get_scan_statistics'
] 