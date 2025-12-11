import os
import logging
from flask import Flask
from flask_pymongo import PyMongo
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

mongo_uri = os.environ.get("MONGO_URI", "mongodb://localhost:27017/caupenrost")
app.config["MONGO_URI"] = mongo_uri
logging.info(f"Using MongoDB at: {mongo_uri}")

mongo = PyMongo(app)

from flask_mail import Mail
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', '587'))
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', '')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', '')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER', '')

mail = Mail(app)

def initialize_database():
    from data_store import init_data_store
    init_data_store()

with app.app_context():
    initialize_database()

from routes import *

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
