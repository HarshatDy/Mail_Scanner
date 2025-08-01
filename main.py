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

from src.config.config_manager import ConfigManager, get_config
from src.utils.logger import get_logger, log_info, log_error


def setup_command(args):
    """Set up the initial configuration for Gmail."""
    logger = get_logger("setup")
    
    try:
        config_manager = ConfigManager()
        config_manager.create_default_config()
        
        logger.info("=== Gmail Email Scanner Setup ===")
        logger.info("Default configuration created. Please edit config.yaml with your settings.")
        logger.info("")
        logger.info("REQUIRED GMAIL SETTINGS:")
        logger.info("1. Enable 2-Factor Authentication on your Google account")
        logger.info("2. Generate a Gmail App Password:")
        logger.info("   - Go to https://myaccount.google.com/security")
        logger.info("   - Enable 2-Step Verification if not already enabled")
        logger.info("   - Go to 'App passwords' (under 2-Step Verification)")
        logger.info("   - Select 'Mail' and generate a password")
        logger.info("")
        logger.info("3. Update config.yaml with:")
        logger.info("   - email.username: Your Gmail address (e.g., yourname@gmail.com)")
        logger.info("   - email.password: The App Password you generated (NOT your regular password)")
        logger.info("   - ai.gemini_api_key: Your Gemini API key from https://makersuite.google.com/app/apikey")
        logger.info("")
        logger.info("4. Optional: Customize filtering settings in config.yaml")
        logger.info("")
        logger.info("After setup, run: python main.py validate")
        
        return True
    except Exception as e:
        log_error(e, "setup")
        return False


def validate_command(args):
    """Validate the current configuration and test Gmail connection."""
    logger = get_logger("validate")
    
    try:
        config_manager = ConfigManager()
        if not config_manager.validate_config():
            logger.error("Configuration validation failed. Please check your settings.")
            return False
        
        logger.info("Configuration is valid!")
        logger.info("Testing Gmail connection...")
        
        # Test Gmail connection
        from email_processing.connector import GmailConnector
        
        connector = GmailConnector()
        if connector.test_connection():
            logger.info("✅ Gmail connection successful!")
            logger.info("✅ Configuration is ready to use.")
            return True
        else:
            logger.error("❌ Gmail connection failed!")
            logger.error("Please check your username and App Password.")
            logger.error("Remember: Use App Password, not your regular Gmail password.")
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
        from src.database.operations import get_statistics
        
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
        from web.app import create_app, create_basic_templates
        
        # Create templates if they don't exist
        create_basic_templates()
        
        app = create_app()
        logger.info(f"Starting web interface on {config.web.host}:{config.web.port}")
        logger.info(f"Open your browser to: http://{config.web.host}:{config.web.port}")
        
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