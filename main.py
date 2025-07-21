#!/usr/bin/env python3
"""
Main CLI script for the Email Scanner & Blog Topic Generator.
Provides command-line interface for running scans, managing configuration, and monitoring the system.
"""

import argparse
import sys
import os
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from config.config_manager import ConfigManager, get_config
from utils.logger import get_logger, log_info, log_error


def setup_command(args):
    """Set up the initial configuration."""
    logger = get_logger("setup")
    
    try:
        config_manager = ConfigManager()
        config_manager.create_default_config()
        
        logger.info("Default configuration created. Please edit config.yaml with your settings.")
        logger.info("Required settings:")
        logger.info("  - email.username: Your email address")
        logger.info("  - email.password: Your email password/app password")
        logger.info("  - ai.gemini_api_key: Your Gemini API key")
        
        return True
    except Exception as e:
        log_error(e, "setup")
        return False


def validate_command(args):
    """Validate the current configuration."""
    logger = get_logger("validate")
    
    try:
        config_manager = ConfigManager()
        if config_manager.validate_config():
            logger.info("Configuration is valid!")
            return True
        else:
            logger.error("Configuration validation failed. Please check your settings.")
            return False
    except Exception as e:
        log_error(e, "validate")
        return False


def scan_command(args):
    """Run a manual email scan."""
    logger = get_logger("scan")
    
    try:
        # Import here to avoid circular imports
        from scheduler.jobs import run_email_scan
        
        logger.info("Starting manual email scan...")
        result = run_email_scan()
        
        if result:
            logger.info("Email scan completed successfully!")
        else:
            logger.error("Email scan failed!")
        
        return result
    except Exception as e:
        log_error(e, "scan")
        return False


def scheduler_command(args):
    """Start the scheduler to run scans automatically."""
    logger = get_logger("scheduler")
    
    try:
        # Import here to avoid circular imports
        from scheduler.main import start_scheduler
        
        logger.info("Starting email scanner scheduler...")
        logger.info("Press Ctrl+C to stop the scheduler")
        
        start_scheduler()
        return True
    except KeyboardInterrupt:
        logger.info("Scheduler stopped by user")
        return True
    except Exception as e:
        log_error(e, "scheduler")
        return False


def status_command(args):
    """Show system status and statistics."""
    logger = get_logger("status")
    
    try:
        # Import here to avoid circular imports
        from database.operations import get_statistics
        
        stats = get_statistics()
        
        print("\n=== Email Scanner Status ===")
        print(f"Total emails processed: {stats.get('total_emails', 0)}")
        print(f"Emails categorized: {stats.get('categorized_emails', 0)}")
        print(f"Topics generated: {stats.get('topics_generated', 0)}")
        print(f"Last scan: {stats.get('last_scan', 'Never')}")
        print(f"Database size: {stats.get('db_size', 'Unknown')}")
        
        return True
    except Exception as e:
        log_error(e, "status")
        return False


def web_command(args):
    """Start the web interface."""
    logger = get_logger("web")
    
    try:
        config = get_config()
        if not config.web.enabled:
            logger.error("Web interface is disabled in configuration")
            return False
        
        # Import here to avoid circular imports
        from web.app import create_app
        
        app = create_app()
        logger.info(f"Starting web interface on {config.web.host}:{config.web.port}")
        
        app.run(
            host=config.web.host,
            port=config.web.port,
            debug=config.web.debug
        )
        
        return True
    except Exception as e:
        log_error(e, "web")
        return False


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Email Scanner & Blog Topic Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py setup                    # Set up initial configuration
  python main.py validate                 # Validate configuration
  python main.py scan                     # Run manual email scan
  python main.py scheduler                # Start automated scheduler
  python main.py status                   # Show system status
  python main.py web                      # Start web interface
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Setup command
    setup_parser = subparsers.add_parser('setup', help='Set up initial configuration')
    setup_parser.set_defaults(func=setup_command)
    
    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate configuration')
    validate_parser.set_defaults(func=validate_command)
    
    # Scan command
    scan_parser = subparsers.add_parser('scan', help='Run manual email scan')
    scan_parser.set_defaults(func=scan_command)
    
    # Scheduler command
    scheduler_parser = subparsers.add_parser('scheduler', help='Start automated scheduler')
    scheduler_parser.set_defaults(func=scheduler_command)
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Show system status')
    status_parser.set_defaults(func=status_command)
    
    # Web command
    web_parser = subparsers.add_parser('web', help='Start web interface')
    web_parser.set_defaults(func=web_command)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Run the selected command
    success = args.func(args)
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main()) 