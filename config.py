import os
from dotenv import load_dotenv
load_dotenv()
class Config:
    """Base config"""
    # API settings
    BASE_URL = os.environ.get('BASE_URL', 'https://openrouter.ai/api/v1')
    OR_API_KEY = os.environ.get('OR_API_KEY', '')
    OR_MODEL = os.environ.get('OR_MODEL', 'google/gemini-2.0-pro-exp-02-05:free')
    REFERER = os.environ.get('REFERER', 'http://localhost')
    TITLE = os.environ.get('TITLE', 'Quiz Generator')
    
    # File paths
    TARGET_DIR = os.environ.get('TARGET_DIR', 'data/output')
    SYSTEM_PROMPT = os.environ.get('SYSTEM_PROMPT', 'prompts/system/default.txt')
    ASSISTANT_PROMPT = os.environ.get('ASSISTANT_PROMPT', 'prompts/assistant/default.txt')
    USER_PROMPT = os.environ.get('USER_PROMPT', 'prompts/user/default.txt')
    SAMPLE_FILE = os.environ.get('SAMPLE_FILE', 'assets/cdmp-sample.txt')
    BOOK_FILE = os.environ.get('BOOK_FILE', 'assets/dmbok.txt')
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY', os.urandom(24).hex())
    DEBUG = False
    TESTING = False

class ProductionConfig(Config):
    """Production config"""
    pass

class DevelopmentConfig(Config):
    """Development config"""
    DEBUG = True

class TestingConfig(Config):
    """Testing config"""
    TESTING = True
    DEBUG = True

# Export config by environment
config_by_name = {
    'dev': DevelopmentConfig,
    'test': TestingConfig,
    'prod': ProductionConfig
}