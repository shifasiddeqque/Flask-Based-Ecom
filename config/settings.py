# app/config/settings.py
import os
class ProductionConfig:
    DEBUG = False
    TESTING = False
    DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI_PROD')

class TestingConfig:
    DEBUG = True
    TESTING = True
    DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI_TESTING')

class DevelopmentConfig:
    DEBUG = True
    TESTING = False
    DATABASE_URI = 'your-development-database-uri'
