# CaupenRost

## Overview
CaupenRost is a Flask-based e-commerce web application for an online bakery. It offers a complete shopping experience with product browsing, cart management, order placement, user authentication, and comprehensive administrative tools. The application uses Indian Rupee (INR) for all transactions and features a custom QR code payment system with screenshot upload proof.

## User Preferences
Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Template Engine**: Jinja2 with Flask.
- **CSS Framework**: Bootstrap 5 for responsiveness.
- **Custom Styling**: CSS custom properties for a bakery theme (brown and cream).
- **JavaScript**: Vanilla JS for interactive elements, Chart.js for analytics, Font Awesome for icons.
- **Typography**: Google Fonts (Playfair Display, Poppins, Dancing Script).
- **UI/UX**: Modernized design with gradients, gold accents, step indicators, animated hero, trust strip, testimonials, category previews.

### Backend Architecture
- **Web Framework**: Flask with modular organization.
- **Session Management**: Flask sessions for cart and authentication.
- **Email System**: Resend API (via `resend` package) — no Gmail/SMTP needed. Uses `RESEND_API_KEY` secret.
- **Data Models**: Object-oriented models for User, Product, Order, Review, Address, Category, Role, OTPCode, Ticket, TicketMessage.
- **Authentication**: Werkzeug password hashing, session-based user management, role-based access control.
- **OTP System**: OTPs stored in MongoDB `otp_codes` collection with TTL index (auto-expire).

### Data Storage
- **Primary**: MongoDB Atlas via `DATABASE_URL` environment variable (mongodb+srv URI).
- **Detection**: `USE_MONGODB = 'mongodb' in DATABASE_URL` (also checks `MONGO_URI`).
- **Collections**: users, products, categories, orders, reviews, addresses, visitor_logs, otp_codes, roles, tickets, ticket_messages.
- **Indexes**: TTL index on `otp_codes.expires_at`, compound indexes on orders/users.

### Application Structure
- `app.py` — Flask app factory, MongoDB index setup, data initialization.
- `routes.py` — All URL routes (1300+ lines).
- `mongo_db.py` — MongoDB repository classes.
- `mongodb_models.py` — MongoDB model classes.
- `data_store.py` — Data seeding (idempotent — skips if data already exists).
- `email_service.py` — OTP generation, storage, and sending via Resend API.
- `utils.py` — Cart helpers, session utilities.

## Key Features

### Admin Panel (`/admin/...`)
- **Dashboard** — Stats, quick actions including "Manage Roles" button.
- **Orders list** (`/admin/orders`) — Table with "View Details" button linking to full order page.
- **Order detail** (`/admin/order/<id>`) — NEW: Full order info, item breakdown with images, payment proof screenshot viewer, customer info, status update form.
- **Users** (`/admin/users`) — Shows role badge per user, assign role modal, toggle admin button.
- **Roles** (`/admin/roles`) — NEW: Create/delete custom roles; system roles (admin, manager, staff, customer) protected from deletion.
- **Products, Categories, Analytics, Support Tickets** — full CRUD.

### Custom Roles System
- Stored in MongoDB `roles` collection.
- System roles: `admin`, `manager`, `staff`, `customer`.
- Custom roles can be created with custom permissions.
- Users have `role` field (string) alongside `is_admin` (bool) for backward compatibility.
- Admins assign roles to users from the Users page (modal dialog).

### Payment Proof Upload
- QR payment page (`/qr_payment`) — Redesigned with drag-and-drop file upload zone.
- Users upload payment screenshot after paying via UPI/QR.
- Saved to `static/uploads/payment_proofs/` as `<order_id>_<hex>.ext`.
- `payment_proof_url` and `payment_proof_uploaded_at` stored in MongoDB order document.
- Order status auto-set to `payment_proof_submitted`.
- Admin sees proof image in order detail page with download link.

### OTPs
- Stored in MongoDB `otp_codes` collection with `expires_at` field.
- TTL index on `expires_at` auto-deletes expired OTPs.
- 10-minute expiry, max 5 attempts before lockout.
- Sent via Resend API (`RESEND_API_KEY` secret).

### Data Seeding (Idempotent)
- `init_data_store()` in `data_store.py` runs on startup.
- Admin user (`admin@caupenrost.com`, password `admin123`) only created if not already in DB.
- Products/categories only seeded if counts are 0.
- MongoDB indexes and system roles created via `setup_indexes()` in `mongo_db.py`.

## External Dependencies

### Python Packages
- **Flask, Flask-SQLAlchemy, Werkzeug** — Core framework.
- **pymongo** — MongoDB driver.
- **resend** — Email sending via Resend API.

### Frontend Libraries (CDN)
- Bootstrap 5, Font Awesome 6, Chart.js, Google Fonts.

### Environment Variables / Secrets
- `DATABASE_URL` — MongoDB Atlas connection string (mongodb+srv://...).
- `RESEND_API_KEY` — Resend API key for email sending.
- `SESSION_SECRET` — Flask session secret key.

### File Storage
- `static/uploads/payment_proofs/` — Payment screenshot uploads.
- `static/images/payment_qr.jpg` — UPI QR code image.
