"""
Development Configuration
For local development environment
"""

import os
from datetime import timedelta

class DevelopmentConfig:
    """Development environment configuration"""
    
    # Flask core
    DEBUG = True
    TESTING = False
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'postgresql://warexpert:warexpert123@localhost:5432/warexpert_db'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = True  # Log all SQL queries in development
    
    # Redis
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    
    # JWT
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'dev-jwt-secret')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=15)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=7)
    JWT_TOKEN_LOCATION = ['headers']
    JWT_HEADER_NAME = 'Authorization'
    JWT_HEADER_TYPE = 'Bearer'
    
    # CORS
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:3000').split(',')
    CORS_ALLOW_CREDENTIALS = True
    
    # File Upload
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'pdf'}
    
    # AWS S3 (disabled in development, use local storage)
    USE_S3 = False
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID', '')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY', '')
    AWS_S3_BUCKET = os.getenv('AWS_S3_BUCKET', '')
    AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
    
    # Email
    SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY', '')
    EMAIL_FROM = os.getenv('EMAIL_FROM', 'noreply@warexpert.com')
    EMAIL_FROM_NAME = os.getenv('EMAIL_FROM_NAME', 'WareXpert')
    
    # Rate Limiting
    RATELIMIT_ENABLED = True
    RATELIMIT_STORAGE_URL = os.getenv('RATELIMIT_STORAGE_URL', 'redis://localhost:6379/1')
    RATELIMIT_DEFAULT = "200 per hour"
    
    # Celery
    CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/2')
    CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/3')
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'DEBUG')
    LOG_FILE = os.getenv('LOG_FILE', 'logs/warexpert.log')
    
    # Application
    DEFAULT_TIMEZONE = os.getenv('DEFAULT_TIMEZONE', 'America/Santiago')
    DEFAULT_CURRENCY = os.getenv('DEFAULT_CURRENCY', 'CLP')
    TAX_RATE = float(os.getenv('TAX_RATE', '19'))  # IVA percentage
    QUOTE_VALID_DAYS = int(os.getenv('QUOTE_VALID_DAYS', '7'))
    
    # Pagination
    ITEMS_PER_PAGE = 24
    MAX_ITEMS_PER_PAGE = 100
