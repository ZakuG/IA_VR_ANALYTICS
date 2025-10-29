"""
Testing Configuration
For unit tests and integration tests
"""

import os
from datetime import timedelta

class TestingConfig:
    """Testing environment configuration"""
    
    # Flask core
    DEBUG = True
    TESTING = True
    SECRET_KEY = 'test-secret-key'
    
    # Database - Use separate test database
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'TEST_DATABASE_URL',
        'postgresql://warexpert:warexpert123@localhost:5432/warexpert_test'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False  # Don't spam test output with SQL
    
    # Redis - Use separate DB for testing
    REDIS_URL = os.getenv('TEST_REDIS_URL', 'redis://localhost:6379/15')
    
    # JWT
    JWT_SECRET_KEY = 'test-jwt-secret'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=15)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=7)
    JWT_TOKEN_LOCATION = ['headers']
    
    # CORS
    CORS_ORIGINS = ['http://localhost:3000']
    
    # File Upload - Use temp directory
    UPLOAD_FOLDER = '/tmp/warexpert_test_uploads'
    USE_S3 = False
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'pdf'}
    
    # Email - Mock in testing
    SENDGRID_API_KEY = 'test-sendgrid-key'
    EMAIL_FROM = 'test@warexpert.com'
    EMAIL_FROM_NAME = 'WareXpert Test'
    
    # Rate Limiting - Disabled in tests
    RATELIMIT_ENABLED = False
    
    # Celery - Use eager mode (synchronous) for tests
    CELERY_TASK_ALWAYS_EAGER = True
    CELERY_TASK_EAGER_PROPAGATES = True
    
    # Logging
    LOG_LEVEL = 'ERROR'  # Only log errors in tests
    
    # Application
    DEFAULT_TIMEZONE = 'America/Santiago'
    DEFAULT_CURRENCY = 'CLP'
    TAX_RATE = 19
    QUOTE_VALID_DAYS = 7
    
    # Pagination
    ITEMS_PER_PAGE = 10  # Smaller for faster tests
    MAX_ITEMS_PER_PAGE = 50
    
    # WTF Forms CSRF - Disable for testing
    WTF_CSRF_ENABLED = False
