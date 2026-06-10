"""
Configuration file for Daily Spend application.

This module contains all configuration settings for different environments
(development, testing, production). Using a centralized config file is a
best practice that allows us to manage settings without hardcoding them
in the application code.

Production-ready practices demonstrated:
- Environment-based configuration (dev/test/prod)
- Sensitive data from environment variables
- Clear separation of concerns
- Commented for maintainability
"""

import os
from datetime import timedelta


class Config:
    """Base configuration class with default settings."""
    
    # Flask Settings
    DEBUG = False
    TESTING = False
    
    # Secret key for session signing (must be set in all environments)
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Session Configuration
    SESSION_COOKIE_SECURE = False  # Will be True in production
    SESSION_COOKIE_HTTPONLY = True  # Prevents JavaScript from accessing cookies
    SESSION_COOKIE_SAMESITE = 'Lax'  # CSRF protection
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    
    # MySQL Database Configuration
    # In production, these should come from environment variables or a secrets manager
    MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
    MYSQL_USER = os.getenv('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', '')
    MYSQL_DB = os.getenv('MYSQL_DB', 'dailyspend')
    
    # Application Settings
    ITEMS_PER_PAGE = 10  # Pagination setting for expense listings


class DevelopmentConfig(Config):
    """Development environment configuration."""
    DEBUG = True
    # In dev, allow less secure session cookies for easier testing
    SESSION_COOKIE_SECURE = False


class TestingConfig(Config):
    """Testing environment configuration."""
    TESTING = True
    # Use in-memory or test database
    MYSQL_DB = 'dailyspend_test'


class ProductionConfig(Config):
    """Production environment configuration."""
    # In production, all security settings should be strict
    SESSION_COOKIE_SECURE = True  # Only send cookies over HTTPS
    
    # Production database credentials should come from environment variables
    MYSQL_HOST = os.getenv('MYSQL_HOST')
    MYSQL_USER = os.getenv('MYSQL_USER')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD')
    MYSQL_DB = os.getenv('MYSQL_DB')
    
    # Ensure all required env vars are set
    if not all([MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB]):
        raise ValueError(
            "Missing required environment variables for production: "
            "MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB"
        )


# Configuration dictionary to easily switch between environments
config_dict = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}


def get_config(env=None):
    """
    Get configuration class based on environment.
    
    Args:
        env (str, optional): Environment name. If None, uses FLASK_ENV variable.
    
    Returns:
        Config: Configuration class for the specified environment.
    """
    if env is None:
        env = os.getenv('FLASK_ENV', 'development')
    
    return config_dict.get(env, config_dict['default'])
