# CaupenRost — Artisan Bakery App

## Overview
CaupenRost is a Flask-based bakery e-commerce website. It supports browsing products, adding items to a cart, placing orders via OTP-verified checkout, and an admin dashboard for managing the store.

## Architecture
- **Backend**: Python/Flask with Jinja2 templating
- **Database**: PostgreSQL via Flask-SQLAlchemy (also supports MongoDB via environment variable)
- **Auth**: Custom session-based authentication with OTP email verification
- **Email**: Resend API (`RESEND_API_KEY`) — falls back to logging OTPs when key is not set
- **Frontend**: Vanilla JS + CSS served as static files

## Project Structure
- `app.py` — Flask app factory, database setup, context processors
- `main.py` — Entry point (`from app import app`)
- `routes.py` — All URL routes and view logic (~1600 lines)
- `models.py` — SQLAlchemy models (User, Product, Order, Category, etc.)
- `db.py` — SQLAlchemy repository pattern classes
- `mongo_db.py` / `mongodb_models.py` — MongoDB equivalent repositories
- `data_store.py` / `init_data.py` — Data seeding and initialization
- `email_service.py` — OTP generation, storage, and Resend email sending
- `utils.py` — Cart helpers, user session utilities
- `config.py` — Config classes (Development, Production, Local)
- `templates/` — Jinja2 HTML templates (admin/, auth/, support/, user/)
- `static/` — CSS, JS, and image assets

## Environment Variables
- `SESSION_SECRET` — Flask secret key (set via Replit secrets)
- `DATABASE_URL` / `PGHOST`, `PGPORT`, `PGUSER`, `PGPASSWORD`, `PGDATABASE` — PostgreSQL connection (auto-provided by Replit)
- `RESEND_API_KEY` — Optional; enables transactional email sending via Resend
- `MONGO_URI` — Optional; switches database backend to MongoDB

## Running the App
- **Development**: `python main.py` (starts Flask dev server on port 5000)
- **Production**: `gunicorn --bind 0.0.0.0:5000 main:app`

## Key Routes
- `/` — Homepage
- `/products` — Product listing
- `/product/<id>` — Product detail
- `/cart` — Shopping cart
- `/login`, `/register` — Auth pages (OTP-based)
- `/checkout` — Order placement
- `/admin` — Admin dashboard (admin users only)
- `/support` — Customer support ticketing
