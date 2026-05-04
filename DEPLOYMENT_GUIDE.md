# CaupenRost — Deployment Guide

> Artisan Bakery E-Commerce · Flask + MongoDB · Dual-Server Architecture

---

## Architecture Overview

CaupenRost runs as **two servers**:

| Server | Port | Role | Command |
|--------|------|------|---------|
| **Frontend** | 5000 | HTML pages (Jinja2) + `/api/*` JSON endpoints | `python3 -m gunicorn --bind 0.0.0.0:5000 main:app` |
| **API Server** | 8080 | Pure JSON REST API, CORS-enabled, MongoDB cart | `python3 -m gunicorn --bind 0.0.0.0:8080 'api_server:api_app'` |

**Database:** MongoDB (primary) with PostgreSQL/SQLite fallback  
**Email:** Resend API (OTP verification, order confirmations)  
**Cart storage:** Flask session (frontend) · MongoDB `api_carts` collection (API server)

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `SESSION_SECRET` | ✅ Yes | Flask session signing key — use a long random string |
| `MONGO_URI` | ✅ Recommended | MongoDB Atlas connection string |
| `RESEND_API_KEY` | Optional | Enables real email delivery for OTPs |
| `DATABASE_URL` | Optional | PostgreSQL URL (fallback if MONGO_URI not set) |

> If neither `MONGO_URI` nor `DATABASE_URL` is set, the app falls back to SQLite at `/tmp/app.db`.

---

## Local Development Setup

### Prerequisites
- Python 3.11+
- Git
- MongoDB Atlas account (or local MongoDB)

### Quick Start

```bash
# Clone the repo
git clone https://github.com/CHIRAG4011/CaupenRost.git
cd CaupenRost

# Install dependencies
pip install -r requirements.txt

# Copy and fill in environment variables
cp .env.example .env
# Edit .env with your values

# Start the frontend server (port 5000)
python3 -m gunicorn --bind 0.0.0.0:5000 --reload main:app

# In a separate terminal — start the API server (port 8080)
python3 -m gunicorn --bind 0.0.0.0:8080 --reload 'api_server:api_app'
```

### .env File

```env
SESSION_SECRET=your-super-secret-key-change-this-to-something-long
MONGO_URI=mongodb+srv://<user>:<pass>@cluster.mongodb.net/Caupenrost
RESEND_API_KEY=re_xxxxxxxxxxxxxxxxxxxx
```

### Accessing the App

| URL | Description |
|-----|-------------|
| http://localhost:5000 | Main storefront |
| http://localhost:5000/admin | Admin dashboard |
| http://localhost:5000/products | Product listing |
| http://localhost:5000/api/health | Frontend API health |
| http://localhost:8080/api/health | Standalone API health |

### Default Admin Credentials
- **Email:** `admin@caupenrost.com`
- **Password:** `admin123`

> Change these immediately in the Admin → Users panel after first login.

---

## API Endpoints Reference

All endpoints return JSON. The `/api/*` routes are available on **both** port 5000 (same-origin, session-backed cart) and port 8080 (CORS-enabled, MongoDB-backed cart).

### Health
```
GET /api/health
```

### Products
```
GET /api/products              # List all products (supports ?q= and ?category=)
GET /api/products/<id>         # Get single product
```

### Categories
```
GET /api/categories            # List active categories
```

### Cart (frontend — port 5000, session-based)
```
GET  /api/cart                 # Get cart contents
POST /api/cart/add/<id>        # Add item  — body: {"quantity": 1}
POST /api/cart/update          # Update qty — body: {"product_id": "...", "quantity": 2}
POST /api/cart/remove/<id>     # Remove item
```

### Cart (API server — port 8080, MongoDB-based, CORS enabled)
Same paths as above. Cart is identified by `api_cart_id` cookie returned in responses.

---

## Deploying to Replit (Current Environment)

The project is already configured for Replit with two workflows:

1. **Start application** — Frontend server on port 5000 (webview)
2. **API Server** — Standalone API server on port 8080 (console)

### Steps to Deploy on a New Replit

1. Import from GitHub: `https://github.com/CHIRAG4011/CaupenRost`
2. Add Secrets (Replit Secrets tab):
   - `SESSION_SECRET` — random 32+ character string
   - `MONGO_URI` — your MongoDB Atlas URI
   - `RESEND_API_KEY` — your Resend API key
3. The `python_database` integration provides `DATABASE_URL` automatically
4. Click **Run** — both workflows start automatically

### Replit Deployment (Publish)

```
Deployment target: Autoscale
Run command: gunicorn --bind 0.0.0.0:5000 main:app
```

> The standalone API server (port 8080) should be deployed separately or the frontend's built-in `/api/*` routes used for production.

---

## Deploying to Vercel

Vercel runs Python as serverless functions. Only the frontend Flask app is supported (not the port 8080 API server).

### vercel.json (already in repo)
```json
{
  "version": 2,
  "builds": [{ "src": "main.py", "use": "@vercel/python" }],
  "routes": [{ "src": "/(.*)", "dest": "main.py" }]
}
```

### Steps
1. Install Vercel CLI: `npm i -g vercel`
2. Run `vercel` in the project root
3. Set environment variables in Vercel dashboard:
   - `SESSION_SECRET`
   - `MONGO_URI`
   - `RESEND_API_KEY`

> **Note:** Vercel serverless functions share no memory between requests. The app uses MongoDB for persistence which is compatible with serverless. Flask sessions (cart) use signed cookies so they work correctly.

---

## Deploying to Railway / Render / Fly.io

These platforms support long-running processes — ideal for running both servers.

### Railway

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway init
railway up
```

Set environment variables in the Railway dashboard.

**Start command:** `python3 -m gunicorn --bind 0.0.0.0:$PORT main:app`

### Render

1. Connect your GitHub repo at render.com
2. Create a **Web Service**
3. **Build command:** `pip install -r requirements.txt`
4. **Start command:** `python3 -m gunicorn --bind 0.0.0.0:$PORT main:app`
5. Add environment variables in Render dashboard

For the API server, create a second Web Service with:
- **Start command:** `python3 -m gunicorn --bind 0.0.0.0:$PORT 'api_server:api_app'`

### Fly.io

```bash
# Install flyctl
curl -L https://fly.io/install.sh | sh

fly launch
fly secrets set SESSION_SECRET=... MONGO_URI=... RESEND_API_KEY=...
fly deploy
```

---

## Deploying to Heroku

```bash
# Login
heroku login

# Create app
heroku create caupenrost

# Set config vars
heroku config:set SESSION_SECRET=your-secret
heroku config:set MONGO_URI=your-mongo-uri
heroku config:set RESEND_API_KEY=your-resend-key

# Deploy
git push heroku main
```

**Procfile** (already in repo):
```
web: gunicorn --bind 0.0.0.0:$PORT main:app
```

---

## MongoDB Collections Reference

The app uses MongoDB (database: `Caupenrost`) with the following collections:

| Collection | Docs | Key Fields |
|------------|------|------------|
| `users` | user accounts | `username`, `email`, `password_hash`, `is_admin`, `role` |
| `products` | product catalogue | `name`, `price`, `category`, `stock`, `image_url`, `is_available` |
| `categories` | product categories | `name`, `description`, `image_url`, `is_active` |
| `orders` | customer orders | `user_id`, `items`, `total`, `status`, `payment_method`, `shipping_address` |
| `addresses` | delivery addresses | `user_id`, `name`, `phone`, `line1`, `city`, `state`, `pincode` |
| `reviews` | product reviews | `product_id`, `user_id`, `rating`, `comment` |
| `productreviews` | product reviews (v2) | `product_id`, `user_id`, `rating`, `comment` |
| `tickets` | support tickets | `user_id`, `order_id`, `subject`, `status`, `priority` |
| `ticket_messages` | ticket replies | `ticket_id`, `author_id`, `message`, `is_admin_reply` |
| `coupons` | discount codes | `code`, `discount_type`, `discount_value`, `min_order`, `expires_at` |
| `announcements` | site banners | `title`, `message`, `is_active`, `priority` |
| `settings` | site config | `key`, `value` (site name, hero text, contact info, etc.) |
| `roles` | admin roles | `name`, `description`, `permissions`, `is_system` |
| `purchases` | payment records | `order_id`, `user_id`, `amount`, `payment_method`, `status` |
| `otps` / `otp_codes` | OTP codes | `email`, `otp`, `purpose`, `expires_at`, `attempts` |
| `visitor_logs` | analytics | `ip_address`, `user_agent`, `page`, `timestamp` |
| `api_carts` | API server carts | `cart_id`, `items` (created by the port 8080 API server) |

### OTP Verification Flow

The app uses **Resend** to email 6-digit OTPs for:
- **Registration** — verify email before account creation
- **Login** — verify identity on each login
- **Order placement** — confirm order before processing

If `RESEND_API_KEY` is not set, OTPs are printed to the server logs (development mode).

---

## Project File Structure

```
CaupenRost/
├── main.py              # Entry point — imports Flask app
├── app.py               # Flask app factory, DB setup, context processors
├── routes.py            # All HTML page routes (~1600 lines)
├── api_routes.py        # JSON API routes registered on main app (/api/*)
├── api_server.py        # Standalone API Flask app (port 8080, CORS enabled)
├── models.py            # SQLAlchemy models (PostgreSQL/SQLite)
├── db.py                # SQLAlchemy repository classes
├── mongo_db.py          # MongoDB repository classes
├── mongodb_models.py    # MongoDB model wrappers
├── data_store.py        # DB abstraction layer (switches between SQL/Mongo)
├── utils.py             # Cart logic, auth helpers (session-based)
├── email_service.py     # Resend email sender, OTP generation/verification
├── config.py            # Environment-based Flask config
├── init_data.py         # Seeds DB with admin user + sample products
├── static/
│   ├── css/style.css    # Main stylesheet
│   ├── css/admin.css    # Admin panel styles
│   ├── js/cart.js       # Cart manager (uses /api/cart/* JSON endpoints)
│   └── js/main.js       # UI animations, particles, review slider
├── templates/           # Jinja2 HTML templates
│   ├── index.html       # Homepage
│   ├── admin/           # Admin dashboard templates
│   ├── auth/            # Login / register / OTP verification
│   ├── support/         # Support ticket templates
│   └── user/            # Profile, orders, addresses
├── requirements.txt     # Python dependencies
├── Procfile             # Heroku start command
└── vercel.json          # Vercel serverless config
```

---

## Updating & Maintenance

### Seed / Re-seed the Database
```bash
python3 init_data.py
```

### Push Code Changes to GitHub
```bash
git add .
git commit -m "your message"
git push origin main
```

### Install New Dependencies
```bash
pip install <package>
pip freeze > requirements.txt
```

---

## Troubleshooting

| Problem | Cause | Fix |
|---------|-------|-----|
| `gunicorn: command not found` | Not on PATH | Use `python3 -m gunicorn ...` |
| `Bad database name "Caupenrost "` | Trailing space in MONGO_URI | Trim the URI in your secrets panel |
| OTPs only appear in logs | `RESEND_API_KEY` not set | Add the key to your environment secrets |
| Cart empty after API call | Different server / session | Use same-origin `/api/cart/*` on port 5000 for session-backed cart |
| 500 on `/api/health` (port 8080) | PyMongo `bool()` check | Fixed — use `db is not None` |
| Static files 404 on Vercel | Vercel doesn't serve `/static/` | Add static route or use CDN |
