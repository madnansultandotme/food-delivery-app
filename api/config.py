import os
from datetime import timedelta

class Config:
    """Base configuration"""
    # Flask config
    DEBUG = False
    TESTING = False
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv('SUPABASE_POSTGRES_URL', 'postgresql://localhost/courier_db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_size": 10,
        "pool_recycle": 3600,
        "pool_pre_ping": True,
    }
    
    # JWT
    JWT_SECRET_KEY = os.getenv('SUPABASE_JWT_SECRET', 'your-secret-key-change-this')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # Security
    CORS_ORIGINS = ['http://localhost:3000', 'http://localhost:3001', os.getenv('FRONTEND_URL', '*')]
    
    # API
    API_TITLE = "Courier Delivery API"
    API_VERSION = "v1"
    API_DESCRIPTION = "Production-ready courier delivery platform API"
    
    # Rate limiting
    RATELIMIT_STORAGE_URL = os.getenv('REDIS_URL', 'memory://')
    
    # Cache
    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = 300

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
}

def get_config():
    """Get config based on environment"""
    env = os.getenv('FLASK_ENV', 'production')
    return config_by_name.get(env, ProductionConfig)
