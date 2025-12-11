"""
Configuration classes for CaupenRost application.
Supports both local development (SQLite) and production (PostgreSQL).
"""
import os


class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SESSION_SECRET', 'dev-secret-key-change-in-production')
    
    # Mail configuration (Gmail SMTP)
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', '587'))
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', '')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', '')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', '')
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }


class DevelopmentConfig(Config):
    """Development configuration - uses SQLite by default"""
    DEBUG = True
    
    @property
    def SQLALCHEMY_DATABASE_URI(self):
        # Check for PostgreSQL configuration first
        database_url = os.environ.get('DATABASE_URL')
        if database_url:
            return database_url
        
        # Check for individual PostgreSQL variables
        pg_host = os.environ.get('PGHOST')
        pg_port = os.environ.get('PGPORT', '5432')
        pg_user = os.environ.get('PGUSER')
        pg_password = os.environ.get('PGPASSWORD')
        pg_database = os.environ.get('PGDATABASE')
        
        if pg_host and pg_user and pg_password and pg_database:
            return f"postgresql://{pg_user}:{pg_password}@{pg_host}:{pg_port}/{pg_database}"
        
        # Default to SQLite for local development
        return 'sqlite:///instance/caupenrost.db'


class ProductionConfig(Config):
    """Production configuration - requires PostgreSQL"""
    DEBUG = False
    
    @property
    def SQLALCHEMY_DATABASE_URI(self):
        database_url = os.environ.get('DATABASE_URL')
        if database_url:
            return database_url
        
        pg_host = os.environ.get('PGHOST')
        pg_port = os.environ.get('PGPORT', '5432')
        pg_user = os.environ.get('PGUSER')
        pg_password = os.environ.get('PGPASSWORD')
        pg_database = os.environ.get('PGDATABASE')
        
        if pg_host and pg_user and pg_password and pg_database:
            return f"postgresql://{pg_user}:{pg_password}@{pg_host}:{pg_port}/{pg_database}"
        
        raise ValueError("DATABASE_URL or PostgreSQL variables must be set in production")


class LocalConfig(Config):
    """Local development configuration - SQLite only, minimal setup"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///instance/caupenrost.db'
    
    # Simplified engine options for SQLite
    SQLALCHEMY_ENGINE_OPTIONS = {}


# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'local': LocalConfig,
    'default': DevelopmentConfig
}


def get_config():
    """Get configuration based on FLASK_ENV environment variable"""
    env = os.environ.get('FLASK_ENV', 'development')
    return config.get(env, config['default'])()
