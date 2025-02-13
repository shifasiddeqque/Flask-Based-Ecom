import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')  # Secret key for your app's security
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Disable SQLAlchemy modification tracking
    CSRF_ENABLED = True  # Enable CSRF protection globally
    CSRF_SESSION_KEY = os.getenv('CSRF_SESSION_KEY', 'a-dummy-csrf-session-key')  # Session key for CSRF (optional)
    WTF_CSRF_SECRET_KEY = os.getenv('WTF_CSRF_SECRET_KEY', 'a-dummy-wtf-csrf-secret-key')  # Secret key for CSRF token signing
    SESSION_PERMANENT = True  # Keeps sessions persistent
    SESSION_TYPE = 'filesystem'  # Can be 'redis', 'filesystem', etc.
    flat_shipping_rate = 100
    flat_tax_rate = 5
    #SESSION_REDIS = redis.StrictRedis(host='localhost', port=6379, db=0) 

class DevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI_DEV')
    DEBUG = True
    PER_PAGE = 6  # Default number of items per page

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI_PROD')
    DEBUG = False
    PER_PAGE = 16  # More items per page in production

class TestingConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI_TESTING')
    TESTING = True
    PER_PAGE = 15  # Adjust items per page for testing

class MailConfig(Config):
    smtp_server = os.getenv('MAIL_SERVER')
    smtp_port = 587
    username = os.getenv('MAIL_USERNAME')
    password = os.getenv('MAIL_PASSWORD')
    sender_email = os.getenv('MAIL_SENDER')
