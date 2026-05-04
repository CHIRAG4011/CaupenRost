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
        sqlite_dir = '/tmp' if os.path.isdir('/tmp') and os.access('/tmp', os.W_OK) else os.path.join(os.path.abspath(os.path.dirname(__file__)), 'instance')
        os.makedirs(sqlite_dir, exist_ok=True)
        database_url = f"sqlite:///{os.path.join(sqlite_dir, 'app.db')}"

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


def initialize_database():
    from data_store import init_data_store
    init_data_store()


with app.app_context():
    if not USE_MONGODB:
        import models  # noqa: F401
        db.create_all()
    else:
        try:
            from mongo_db import setup_indexes
            setup_indexes()
        except Exception as e:
            logging.warning(f"Index setup failed: {e}")
    initialize_database()

from email_service import log_startup_config
log_startup_config()

SETTING_DEFAULTS = {
    'site_name': 'CaupenRost',
    'site_tagline': 'Freshly baked goods made with love',
    'contact_phone': '+91 7016377439',
    'contact_email': 'hello@caupenrost.com',
    'hero_badge': 'Trusted by 1000+ Happy Customers',
    'hero_title': 'Freshly Baked',
    'hero_highlight': 'Happiness',
    'hero_title_end': 'Delivered',
    'hero_subtitle': 'Discover the magic of artisan baked goods made with love, premium ingredients, and traditional recipes passed down through generations.',
    'free_delivery_min': '500',
    'about_year': 'Since 2020',
    'about_lead': 'CaupenRost began with a simple dream - to bring the joy of freshly baked goods to every home.',
    'about_text': 'What started as a small home bakery has grown into a beloved community treasure. Our passion for baking and commitment to quality ingredients sets us apart. Every item is made with traditional techniques and the finest ingredients sourced locally.',
    'cta_title': 'Ready to Taste the Difference?',
    'cta_subtitle': 'Order now and experience the joy of freshly baked goodness delivered to your doorstep!',
    'footer_text': '© 2025 CaupenRost. Made with love in India. All rights reserved.',
    'testimonial_1_name': 'Priya Sharma',
    'testimonial_1_role': 'Regular Customer',
    'testimonial_1_text': 'The chocolate truffle cake was absolutely divine! Fresh, moist, and perfectly sweet. Will definitely order again for every celebration!',
    'testimonial_1_img': 'https://images.unsplash.com/photo-1607746882042-944635dfe10e?ixlib=rb-4.0.3&auto=format&fit=crop&w=150&q=80',
    'testimonial_2_name': 'Rahul Mehta',
    'testimonial_2_role': 'Food Enthusiast',
    'testimonial_2_text': 'Best bakery in town! The croissants are flaky and buttery just like in Paris. Quick delivery and excellent packaging too.',
    'testimonial_2_img': '/static/images/testimonial_saree_woman.png',
    'testimonial_3_name': 'Anita Desai',
    'testimonial_3_role': 'Happy Parent',
    'testimonial_3_text': 'Ordered a custom birthday cake and it exceeded all expectations! Beautiful design and the taste was even better. Highly recommend!',
    'testimonial_3_img': 'https://images.unsplash.com/photo-1438761681033-6461ffad8d80?ixlib=rb-4.0.3&auto=format&fit=crop&w=150&q=80',
}

@app.context_processor
def inject_active_announcement():
    """Inject the top active announcement and site settings into all templates"""
    try:
        if USE_MONGODB:
            from mongo_db import MongoAnnouncementRepo
            active = MongoAnnouncementRepo.find_active()
            top_announcement = active[0] if active else None
        else:
            top_announcement = None
    except:
        top_announcement = None

    site_settings = dict(SETTING_DEFAULTS)
    if USE_MONGODB:
        try:
            from mongo_db import MongoSettingRepo
            saved = MongoSettingRepo.get_all()
            if saved:
                site_settings.update(saved)
        except Exception as e:
            logging.warning(f"Settings fetch failed: {e}")

    return {'top_announcement': top_announcement, 'site_settings': site_settings}


from routes import *
import api_routes  # noqa: F401 — registers /api/* JSON endpoints

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
