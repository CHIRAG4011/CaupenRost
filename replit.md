# CaupenRost — Artisan Bakery App

## Overview
CaupenRost is a Flask-based bakery e-commerce website. It supports browsing products, adding items to a cart, placing orders via OTP-verified checkout, and an admin dashboard for managing the store.

## UI Theme (last updated May 2026)
- **Color palette**: Warm dark mahogany backgrounds (`#080604`, `#1a0f07`) with burnt orange/terracotta accent (`#e07832`) replacing the previous yellow-gold. Warm cream text (`#f6e8d5`).
- **Custom cursor**: Croissant emoji 🥐 cursor with a glowing orange trail (desktop only).
- **Mobile touch**: Orange radial ripple effect on every touch event.
- **Review slider**: Auto-sliding carousel with swipe support, prev/next buttons, and dot indicators. Replaces static review grid. Falls back to a "Be first to review" CTA when no reviews.
- **Clickable product cards**: Entire card navigates to product detail. Add-to-cart buttons stop event propagation.
- **Animations**: Hero fade-up entrance, feature card pulse glow, button shimmer slides.
- **Admin**: Prominent "Back to Site" branded button in topbar. Customer Testimonials section removed from settings page. Coupons stat cards use correct `.admin-stat-num` CSS class.

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
