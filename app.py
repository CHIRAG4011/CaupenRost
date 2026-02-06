import os
import logging
from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

db = None
USE_MONGODB = bool(os.environ.get('MONGO_URI')) or (os.environ.get('DATABASE_URL') and 'mongodb' in os.environ.get('DATABASE_URL'))

if USE_MONGODB:
    logging.info("MongoDB mode enabled")
    try:
        from mongo_db import get_mongo_db
        mongo_db = get_mongo_db()
        logging.info("MongoDB connection established successfully")
    except Exception as e:
        logging.error(f"Failed to connect to MongoDB: {e}")
        USE_MONGODB = False
        logging.info("Falling back to SQLAlchemy due to MongoDB connection failure")

if not USE_MONGODB:
    from flask_sqlalchemy import SQLAlchemy
    from sqlalchemy.orm import DeclarativeBase

    class Base(DeclarativeBase):
        pass

    db = SQLAlchemy(model_class=Base)

    database_url = os.environ.get("DATABASE_URL")
    if database_url and 'mongodb' in database_url:
        database_url = None # Force fallback for SQLAlchemy
    
    if not database_url:
        pg_host = os.environ.get("PGHOST")
        pg_port = os.environ.get("PGPORT", "5432")
        pg_user = os.environ.get("PGUSER")
        pg_password = os.environ.get("PGPASSWORD", "")
        pg_database = os.environ.get("PGDATABASE")
        if pg_host and pg_user and pg_database:
            from urllib.parse import quote_plus
            password_encoded = quote_plus(pg_password) if pg_password else ""
            database_url = f"postgresql://{pg_user}:{password_encoded}@{pg_host}:{pg_port}/{pg_database}"

    if not database_url:
        logging.warning("DATABASE_URL not set, using SQLite as fallback")
        basedir = os.path.abspath(os.path.dirname(__file__))
        os.makedirs(os.path.join(basedir, 'instance'), exist_ok=True)
        database_url = f"sqlite:///{os.path.join(basedir, 'instance', 'app.db')}"

    logging.info(f"Using database URL: {database_url[:50]}..." if len(database_url) > 50 else f"Using database URL: {database_url}")

    app.config["SQLALCHEMY_DATABASE_URI"] = database_url

    if database_url.startswith("sqlite"):
        app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {}
    else:
        app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
            "pool_recycle": 300,
            "pool_pre_ping": True,
        }

    db.init_app(app)

from flask_mail import Mail
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', '587'))
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = (os.environ.get('MAIL_USERNAME') or os.environ.get('GMAIL_EMAIL') or '').strip()
app.config['MAIL_PASSWORD'] = (os.environ.get('MAIL_PASSWORD') or os.environ.get('GMAIL_APP_PASSWORD') or '').strip()
app.config['MAIL_DEFAULT_SENDER'] = (os.environ.get('MAIL_DEFAULT_SENDER') or app.config['MAIL_USERNAME']).strip()

mail = Mail(app)


def initialize_database():
    from data_store import init_data_store
    init_data_store()


with app.app_context():
    if not USE_MONGODB:
        import models  # noqa: F401
        db.create_all()
    initialize_database()

from routes import *

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
