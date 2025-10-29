"""
Production Configuration
For production environment (staging/production)
"""

import os
from datetime import timedelta

class ProductionConfig:
    """Production environment configuration"""
    
    # Flask core
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.getenv('SECRET_KEY') or 'fallback-key-for-import'  # MUST be set in production
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL') or 'postgresql://localhost/warexpert'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False  # Don't log SQL in production
    SQLALCHEMY_POOL_SIZE = 10
    SQLALCHEMY_POOL_RECYCLE = 3600
    
    # Redis
    REDIS_URL = os.getenv('REDIS_URL') or 'redis://localhost:6379/0'
    
    # JWT
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY') or 'fallback-jwt-key'
    
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=15)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=7)
    JWT_TOKEN_LOCATION = ['headers']
    JWT_HEADER_NAME = 'Authorization'
    JWT_HEADER_TYPE = 'Bearer'
    
    # CORS
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '').split(',')
    CORS_ALLOW_CREDENTIALS = True
    
    # File Upload - Use S3 in production
    USE_S3 = True
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    AWS_S3_BUCKET = os.getenv('AWS_S3_BUCKET')
    AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
    
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'pdf'}
    
    # Email
    SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')
    EMAIL_FROM = os.getenv('EMAIL_FROM', 'noreply@warexpert.com')
    EMAIL_FROM_NAME = os.getenv('EMAIL_FROM_NAME', 'WareXpert')
    
    # Rate Limiting
    RATELIMIT_ENABLED = True
    RATELIMIT_STORAGE_URL = os.getenv('RATELIMIT_STORAGE_URL')
    RATELIMIT_DEFAULT = "100 per hour"  # More restrictive in production
    
    # Celery
    CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL')
    CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND')
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'logs/warexpert.log')
    
    # Application
    DEFAULT_TIMEZONE = os.getenv('DEFAULT_TIMEZONE', 'America/Santiago')
    DEFAULT_CURRENCY = os.getenv('DEFAULT_CURRENCY', 'CLP')
    TAX_RATE = float(os.getenv('TAX_RATE', '19'))
    QUOTE_VALID_DAYS = int(os.getenv('QUOTE_VALID_DAYS', '7'))
    
    # Pagination
    ITEMS_PER_PAGE = 24
    MAX_ITEMS_PER_PAGE = 100
    
    # Security
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
