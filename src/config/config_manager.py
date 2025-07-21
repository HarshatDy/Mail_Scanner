"""
Configuration manager for the Email Scanner system.
Handles loading and validating configuration from YAML files.
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class EmailConfig(BaseModel):
    """Email configuration settings."""
    provider: str = "gmail"
    username: str = ""
    password: str = ""
    imap_server: str = "imap.gmail.com"
    imap_port: int = 993
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    use_ssl: bool = True
    use_oauth2: bool = True
    
    # Filtering rules
    exclude_domains: list = Field(default_factory=list)
    exclude_keywords: list = Field(default_factory=list)
    include_categories: list = Field(default_factory=lambda: ["tech", "newsletter", "social", "professional"])


class DatabaseConfig(BaseModel):
    """Database configuration settings."""
    type: str = "sqlite"
    url: str = "sqlite:///data/emails.db"
    echo: bool = False
    pool_size: int = 10
    max_overflow: int = 20


class AIConfig(BaseModel):
    """AI configuration settings."""
    provider: str = "gemini"
    gemini_api_key: str = ""
    openai_api_key: str = ""
    model: str = "gemini-pro"
    max_tokens: int = 1000
    temperature: float = 0.7
    
    # Topic generation settings
    max_topics_per_scan: int = 10
    min_content_length: int = 100
    relevance_threshold: float = 0.7
    categories: list = Field(default_factory=lambda: [
        "Technology Trends",
        "Programming & Development", 
        "AI & Machine Learning",
        "Startup & Business",
        "Productivity & Tools"
    ])


class SchedulerConfig(BaseModel):
    """Scheduler configuration settings."""
    scan_times: list = Field(default_factory=lambda: ["09:00", "18:00"])
    timezone: str = "UTC"
    max_retries: int = 3
    retry_delay: int = 300


class NotificationConfig(BaseModel):
    """Notification configuration settings."""
    enabled: bool = True
    email_notifications: bool = True
    slack_webhook: str = ""
    discord_webhook: str = ""
    
    # Notification triggers
    new_topics: bool = True
    errors: bool = True
    scan_complete: bool = False
    weekly_summary: bool = True


class LoggingConfig(BaseModel):
    """Logging configuration settings."""
    level: str = "INFO"
    file: str = "logs/email_scanner.log"
    max_size: str = "10MB"
    backup_count: int = 5
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


class ProcessingConfig(BaseModel):
    """Content processing configuration settings."""
    max_email_size: str = "10MB"
    extract_links: bool = True
    extract_attachments: bool = False
    clean_html: bool = True
    remove_duplicates: bool = True
    
    # Content cleaning
    remove_html_tags: bool = True
    remove_urls: bool = False
    remove_emails: bool = True
    remove_phone_numbers: bool = True
    min_word_count: int = 10


class WebConfig(BaseModel):
    """Web interface configuration settings."""
    enabled: bool = False
    host: str = "0.0.0.0"
    port: int = 5000
    debug: bool = False
    secret_key: str = ""


class AppConfig(BaseModel):
    """Main application configuration."""
    email: EmailConfig = Field(default_factory=EmailConfig)
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    ai: AIConfig = Field(default_factory=AIConfig)
    scheduler: SchedulerConfig = Field(default_factory=SchedulerConfig)
    notifications: NotificationConfig = Field(default_factory=NotificationConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    processing: ProcessingConfig = Field(default_factory=ProcessingConfig)
    web: WebConfig = Field(default_factory=WebConfig)


class ConfigManager:
    """Manages application configuration loading and validation."""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or "config.yaml"
        self.config: Optional[AppConfig] = None
    
    def load_config(self) -> AppConfig:
        """Load configuration from YAML file."""
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        
        with open(self.config_path, 'r', encoding='utf-8') as file:
            config_data = yaml.safe_load(file)
        
        # Override with environment variables
        config_data = self._override_with_env(config_data)
        
        # Validate configuration
        self.config = AppConfig(**config_data)
        return self.config
    
    def _override_with_env(self, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """Override configuration with environment variables."""
        env_mappings = {
            'EMAIL_USERNAME': ('email', 'username'),
            'EMAIL_PASSWORD': ('email', 'password'),
            'GEMINI_API_KEY': ('ai', 'gemini_api_key'),
            'OPENAI_API_KEY': ('ai', 'openai_api_key'),
            'DATABASE_URL': ('database', 'url'),
            'SLACK_WEBHOOK_URL': ('notifications', 'slack_webhook'),
            'DISCORD_WEBHOOK_URL': ('notifications', 'discord_webhook'),
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
            
            # Check required fields
            if not config.email.username:
                raise ValueError("Email username is required")
            
            if not config.email.password:
                raise ValueError("Email password is required")
            
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
        config_dict = default_config.dict()
        
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