import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

class Config:
    """Base configuration class"""
    SECRET_KEY = os.environ.get('OR_API_KEY', 'dev-key-change-in-production')
    TEMPLATES_FOLDER = 'templates'
    STATIC_FOLDER = 'static'

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    
class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False

# Set configuration based on environment
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}