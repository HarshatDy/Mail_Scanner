"""
Configuration manager for the Email Scanner system.
Handles loading and validating configuration from YAML files.
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv


class EmailConfig:
    """Gmail-specific email configuration settings."""
    
    def __init__(self):
        self.provider = "gmail"
        self.username = ""
        self.password = ""  # Gmail App Password (not regular password)
        self.imap_server = "imap.gmail.com"
        self.imap_port = 993
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.use_ssl = True
        self.use_oauth2 = False  # Set to False for App Password authentication
        
        # Gmail API settings
        self.use_gmail_api = True  # Use Gmail API instead of SMTP/IMAP
        self.credentials_file = "credentials.json"  # Path to Google API credentials
        self.token_file = "token.json"  # Path to store OAuth2 token
        
        # Gmail-specific settings
        self.gmail_labels = ["INBOX", "Primary", "Social", "Promotions"]
        self.max_emails_per_scan = 100
        self.scan_unread_only = False
        self.days_back = 7
        
        # Filtering rules
        self.exclude_domains = []
        self.exclude_keywords = []
        self.include_categories = ["tech", "newsletter", "social", "professional"]
        
        # Gmail API setup instructions
        self.gmail_api_instructions = """
        To use Gmail API with this scanner, you need to:
        1. Go to Google Cloud Console (https://console.cloud.google.com/)
        2. Create a new project or select existing one
        3. Enable Gmail API for your project
        4. Create OAuth 2.0 credentials:
           - Go to APIs & Services > Credentials
           - Click "Create Credentials" > "OAuth 2.0 Client IDs"
           - Choose "Desktop application"
           - Download the credentials.json file
        5. Place credentials.json in the project root directory
        6. Run the application - it will open browser for OAuth2 authorization
        """
    
    def to_dict(self):
        """Convert to dictionary for YAML serialization."""
        return {
            'provider': self.provider,
            'username': self.username,
            'password': self.password,
            'imap_server': self.imap_server,
            'imap_port': self.imap_port,
            'smtp_server': self.smtp_server,
            'smtp_port': self.smtp_port,
            'use_ssl': self.use_ssl,
            'use_oauth2': self.use_oauth2,
            'use_gmail_api': self.use_gmail_api,
            'credentials_file': self.credentials_file,
            'token_file': self.token_file,
            'gmail_labels': self.gmail_labels,
            'max_emails_per_scan': self.max_emails_per_scan,
            'scan_unread_only': self.scan_unread_only,
            'days_back': self.days_back,
            'exclude_domains': self.exclude_domains,
            'exclude_keywords': self.exclude_keywords,
            'include_categories': self.include_categories
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """Create from dictionary."""
        config = cls()
        for key, value in data.items():
            if hasattr(config, key):
                setattr(config, key, value)
        return config


class DatabaseConfig:
    """Database configuration settings."""
    
    def __init__(self):
        self.type = "sqlite"
        self.url = "sqlite:///data/emails.db"
        self.echo = False
        self.pool_size = 10
        self.max_overflow = 20
    
    def to_dict(self):
        return {
            'type': self.type,
            'url': self.url,
            'echo': self.echo,
            'pool_size': self.pool_size,
            'max_overflow': self.max_overflow
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        config = cls()
        for key, value in data.items():
            if hasattr(config, key):
                setattr(config, key, value)
        return config


class AIConfig:
    """AI configuration settings."""
    
    def __init__(self):
        self.provider = "gemini"
        self.gemini_api_key = ""
        self.openai_api_key = ""
        self.model = "gemini-2.0-flash-lite"
        self.max_tokens = 1000
        self.temperature = 0.7
        
        # Topic generation settings
        self.max_topics_per_scan = 10
        self.min_content_length = 100
        self.relevance_threshold = 0.7
        self.categories = [
            "Technology Trends",
            "Programming & Development", 
            "AI & Machine Learning",
            "Startup & Business",
            "Productivity & Tools"
        ]
    
    def to_dict(self):
        return {
            'provider': self.provider,
            'gemini_api_key': self.gemini_api_key,
            'openai_api_key': self.openai_api_key,
            'model': self.model,
            'max_tokens': self.max_tokens,
            'temperature': self.temperature,
            'max_topics_per_scan': self.max_topics_per_scan,
            'min_content_length': self.min_content_length,
            'relevance_threshold': self.relevance_threshold,
            'categories': self.categories
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        config = cls()
        for key, value in data.items():
            if hasattr(config, key):
                setattr(config, key, value)
        return config


class SchedulerConfig:
    """Scheduler configuration settings."""
    
    def __init__(self):
        self.scan_times = ["09:00", "18:00"]
        self.timezone = "UTC"
        self.max_retries = 3
        self.retry_delay = 300
    
    def to_dict(self):
        return {
            'scan_times': self.scan_times,
            'timezone': self.timezone,
            'max_retries': self.max_retries,
            'retry_delay': self.retry_delay
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        config = cls()
        for key, value in data.items():
            if hasattr(config, key):
                setattr(config, key, value)
        return config


class NotificationConfig:
    """Notification configuration settings."""
    
    def __init__(self):
        self.enabled = True
        self.email_notifications = True
        self.notification_email = ""
        self.slack_webhook = ""
        self.discord_webhook = ""
        
        # Notification triggers
        self.new_topics = True
        self.errors = True
        self.scan_complete = False
        self.weekly_summary = True
    
    def to_dict(self):
        return {
            'enabled': self.enabled,
            'email_notifications': self.email_notifications,
            'notification_email': self.notification_email,
            'slack_webhook': self.slack_webhook,
            'discord_webhook': self.discord_webhook,
            'new_topics': self.new_topics,
            'errors': self.errors,
            'scan_complete': self.scan_complete,
            'weekly_summary': self.weekly_summary
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        config = cls()
        for key, value in data.items():
            if hasattr(config, key):
                setattr(config, key, value)
        return config


class LoggingConfig:
    """Logging configuration settings."""
    
    def __init__(self):
        self.level = "INFO"
        self.file = "logs/email_scanner.log"
        self.max_size = "10MB"
        self.backup_count = 5
        self.format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    def to_dict(self):
        return {
            'level': self.level,
            'file': self.file,
            'max_size': self.max_size,
            'backup_count': self.backup_count,
            'format': self.format
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        config = cls()
        for key, value in data.items():
            if hasattr(config, key):
                setattr(config, key, value)
        return config


class ProcessingConfig:
    """Content processing configuration settings."""
    
    def __init__(self):
        self.max_email_size = "10MB"
        self.extract_links = True
        self.extract_attachments = False
        self.clean_html = True
        self.remove_duplicates = True
        
        # Content cleaning
        self.remove_html_tags = True
        self.remove_urls = False
        self.remove_emails = True
        self.remove_phone_numbers = True
        self.min_word_count = 10
    
    def to_dict(self):
        return {
            'max_email_size': self.max_email_size,
            'extract_links': self.extract_links,
            'extract_attachments': self.extract_attachments,
            'clean_html': self.clean_html,
            'remove_duplicates': self.remove_duplicates,
            'remove_html_tags': self.remove_html_tags,
            'remove_urls': self.remove_urls,
            'remove_emails': self.remove_emails,
            'remove_phone_numbers': self.remove_phone_numbers,
            'min_word_count': self.min_word_count
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        config = cls()
        for key, value in data.items():
            if hasattr(config, key):
                setattr(config, key, value)
        return config


class WebConfig:
    """Web interface configuration settings."""
    
    def __init__(self):
        self.enabled = False
        self.host = "0.0.0.0"
        self.port = 5000
        self.debug = False
        self.secret_key = ""
    
    def to_dict(self):
        return {
            'enabled': self.enabled,
            'host': self.host,
            'port': self.port,
            'debug': self.debug,
            'secret_key': self.secret_key
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        config = cls()
        for key, value in data.items():
            if hasattr(config, key):
                setattr(config, key, value)
        return config


class AppConfig:
    """Main application configuration."""
    
    def __init__(self):
        self.email = EmailConfig()
        self.database = DatabaseConfig()
        self.ai = AIConfig()
        self.scheduler = SchedulerConfig()
        self.notifications = NotificationConfig()
        self.logging = LoggingConfig()
        self.processing = ProcessingConfig()
        self.web = WebConfig()
    
    def to_dict(self):
        return {
            'email': self.email.to_dict(),
            'database': self.database.to_dict(),
            'ai': self.ai.to_dict(),
            'scheduler': self.scheduler.to_dict(),
            'notifications': self.notifications.to_dict(),
            'logging': self.logging.to_dict(),
            'processing': self.processing.to_dict(),
            'web': self.web.to_dict()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        config = cls()
        if 'email' in data:
            config.email = EmailConfig.from_dict(data['email'])
        if 'database' in data:
            config.database = DatabaseConfig.from_dict(data['database'])
        if 'ai' in data:
            config.ai = AIConfig.from_dict(data['ai'])
        if 'scheduler' in data:
            config.scheduler = SchedulerConfig.from_dict(data['scheduler'])
        if 'notifications' in data:
            config.notifications = NotificationConfig.from_dict(data['notifications'])
        if 'logging' in data:
            config.logging = LoggingConfig.from_dict(data['logging'])
        if 'processing' in data:
            config.processing = ProcessingConfig.from_dict(data['processing'])
        if 'web' in data:
            config.web = WebConfig.from_dict(data['web'])
        return config


class ConfigManager:
    """Manages application configuration loading and validation."""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or "config.yaml"
        self.config: Optional[AppConfig] = None
    
    def load_config(self) -> AppConfig:
        """Load configuration from YAML file."""
        # Load environment variables from .env file
        load_dotenv()
        
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        
        with open(self.config_path, 'r', encoding='utf-8') as file:
            config_data = yaml.safe_load(file)
        
        # Override with environment variables
        config_data = self._override_with_env(config_data)
        
        # Validate configuration
        self.config = AppConfig.from_dict(config_data)
        return self.config
    
    def _override_with_env(self, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """Override configuration with environment variables."""
        env_mappings = {
            'EMAIL_USERNAME': ('email', 'username'),
            'EMAIL_PASSWORD': ('email', 'password'),
            'EMAIL_IMAP_SERVER': ('email', 'imap_server'),
            'EMAIL_IMAP_PORT': ('email', 'imap_port'),
            'EMAIL_SMTP_SERVER': ('email', 'smtp_server'),
            'EMAIL_SMTP_PORT': ('email', 'smtp_port'),
            'EMAIL_USE_GMAIL_API': ('email', 'use_gmail_api'),
            'EMAIL_CREDENTIALS_FILE': ('email', 'credentials_file'),
            'EMAIL_TOKEN_FILE': ('email', 'token_file'),
            'GEMINI_API_KEY': ('ai', 'gemini_api_key'),
            'OPENAI_API_KEY': ('ai', 'openai_api_key'),
            'DATABASE_URL': ('database', 'url'),
            'SLACK_WEBHOOK_URL': ('notifications', 'slack_webhook'),
            'DISCORD_WEBHOOK_URL': ('notifications', 'discord_webhook'),
            'WEB_SECRET_KEY': ('web', 'secret_key'),
             'NOTIFICATION_EMAIL': ('notifications', 'notification_email'),
        }
        
        for env_var, config_path in env_mappings.items():
            env_value = os.getenv(env_var)
            if env_value:
                # Navigate to the nested config location
                current = config_data
                for key in config_path[:-1]:
                    if key not in current:
                        current[key] = {}
                    current = current[key]
                
                # Convert port numbers to integers
                if config_path[-1] in ['imap_port', 'smtp_port']:
                    try:
                        current[config_path[-1]] = int(env_value)
                    except ValueError:
                        print(f"Warning: Invalid port number for {env_var}: {env_value}")
                        continue
                else:
                    current[config_path[-1]] = env_value
        
        return config_data
    
    def get_config(self) -> AppConfig:
        """Get the current configuration, loading if necessary."""
        if self.config is None:
            self.config = self.load_config()
        return self.config
    
    def reload_config(self) -> AppConfig:
        """Reload configuration from file."""
        self.config = None
        return self.get_config()
    
    def validate_config(self) -> bool:
        """Validate the current configuration."""
        try:
            config = self.get_config()
            
            # Check required fields based on email provider
            if config.email.use_gmail_api:
                # For Gmail API, we need credentials file
                if not os.path.exists(config.email.credentials_file):
                    raise ValueError(f"Gmail API credentials file not found: {config.email.credentials_file}")
            else:
                # For SMTP/IMAP, we need username and password
                if not config.email.username:
                    raise ValueError("Email username is required for SMTP/IMAP")
                
                if not config.email.password:
                    raise ValueError("Email password is required for SMTP/IMAP")
            
            if config.ai.provider == "gemini" and not config.ai.gemini_api_key:
                raise ValueError("Gemini API key is required when using Gemini provider")
            
            if config.ai.provider == "openai" and not config.ai.openai_api_key:
                raise ValueError("OpenAI API key is required when using OpenAI provider")
            
            return True
            
        except Exception as e:
            print(f"Configuration validation failed: {e}")
            return False
    
    def create_default_config(self) -> None:
        """Create a default configuration file if it doesn't exist."""
        if os.path.exists(self.config_path):
            return
        
        default_config = AppConfig()
        
        # Convert to dict for YAML serialization
        config_dict = default_config.to_dict()
        
        # Create directory if it doesn't exist
        config_dir = os.path.dirname(self.config_path)
        if config_dir:
            os.makedirs(config_dir, exist_ok=True)
        
        with open(self.config_path, 'w', encoding='utf-8') as file:
            yaml.dump(config_dict, file, default_flow_style=False, indent=2)
        
        print(f"Default configuration created at: {self.config_path}")


# Global configuration instance
config_manager = ConfigManager()


def get_config() -> AppConfig:
    """Get the global configuration instance."""
    return config_manager.get_config()


def load_config(config_path: Optional[str] = None) -> AppConfig:
    """Load configuration from the specified path."""
    if config_path:
        manager = ConfigManager(config_path)
        return manager.load_config()
    return config_manager.load_config() 