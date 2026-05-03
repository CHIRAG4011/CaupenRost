# CaupenRost

## Overview
CaupenRost is a Flask-based e-commerce web application for an online bakery. It offers a complete shopping experience with product browsing, cart management, order placement, user authentication, and comprehensive administrative tools. The application uses Indian Rupee (INR) for all transactions and features a custom QR code payment system with screenshot upload proof.

## User Preferences
Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Template Engine**: Jinja2 with Flask.
- **CSS Framework**: Bootstrap 5 for responsiveness.
- **Custom Styling**: Full luxury dark editorial theme — `--bg-base:#080605`, gold accents (`--gold:#d4a843`), glassmorphism components, CSS custom properties throughout.
- **JavaScript**: Vanilla JS for interactive elements, Chart.js for analytics, Font Awesome 6 icons.
- **Typography**: Google Fonts — Playfair Display (headings), Poppins/Inter (body).
- **UI/UX**: Ultra-premium dark luxury theme — particle canvas background, glass navbar scroll effect, cinematic hero with CSS animations, CSS 3D holographic tilt card on product detail page (replaces Three.js), premium dark product/category/testimonial/review cards, scroll-reveal animations.

### Admin UI
- All admin pages extend `templates/admin/base_admin.html` — fixed dark sidebar, topbar, gold accent CSS classes.
- Admin CSS classes: `admin-card`, `admin-card-header`, `admin-card-body`, `admin-table`, `status-pill` (with modifiers), `tbl-btn`, `u-avatar`, `quick-action-grid/item`, `admin-stat-card`, `perm-category/grid`, `perm-checkbox/label`.
- Fully redesigned admin pages: dashboard, orders, order_detail, users, roles (94 permissions in 10 categories as checkboxes), products, tickets, view_ticket, categories, add_category, edit_category, analytics, announcements, coupons, settings.

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

## Template Map

### Public / User pages (extend `base.html`)
- `index.html` — Hero, products, about, CTA sections.
- `products.html` — Product listing with filter sidebar.
- `product_detail.html` — CSS 3D holographic tilt card viewer.
- `support/tickets.html` — Support centre listing.
- `support/create_ticket.html` — New ticket form with priority pills and order select.
- `support/view_ticket.html` — Thread view with bubble-style messages.
- `user/profile.html`, `user/orders.html`, `user/order_detail.html` — User account pages.

### Admin pages (extend `admin/base_admin.html`)
- `admin/dashboard.html` — Stats cards + quick actions.
- `admin/orders.html`, `admin/order_detail.html` — Orders management.
- `admin/users.html` — User list with role assignment modal.
- `admin/roles.html` — 94 permissions across 10 categories as checkboxes.
- `admin/products.html` — Product CRUD with hidden `product_id` field in edit modal.
- `admin/categories.html`, `admin/add_category.html`, `admin/edit_category.html` — Category management.
- `admin/analytics.html` — Chart.js visitors + order distribution charts, dark theme.
- `admin/announcements.html` — Live preview, colour pickers, icon picker.
- `admin/coupons.html` — Coupon CRUD with live preview card.
- `admin/settings.html` — Sitewide content settings (hero, about, testimonials, CTA, footer).
- `admin/tickets.html`, `admin/view_ticket.html` — Support ticket management.

## Key Features

### Admin Panel (`/admin/...`)
- **Dashboard** — Stats, quick actions including "Manage Roles" button.
- **Orders list** (`/admin/orders`) — Table with "View Details" button linking to full order page.
- **Order detail** (`/admin/order/<id>`) — Full order info, item breakdown with images, payment proof screenshot viewer, customer info, status update form.
- **Users** (`/admin/users`) — Shows role badge per user, assign role modal, toggle admin button.
- **Roles** (`/admin/roles`) — Create/delete custom roles; system roles (admin, manager, staff, customer) protected from deletion. 94 permissions shown as checkboxes in 10 categories.
- **Products, Categories, Analytics, Support Tickets** — full CRUD.
- **Announcements** — Live preview with colour/icon pickers.
- **Coupons** — Percentage and fixed discount types, live preview card.
- **Settings** — Sitewide content editor (hero, about, testimonials, CTA, footer).

### Custom Roles System
- Stored in MongoDB `roles` collection.
- System roles: `admin`, `manager`, `staff`, `customer`.
- Custom roles can be created with custom permissions (94 checkboxes across 10 categories).
- Users have `role` field (string) alongside `is_admin` (bool) for backward compatibility.
- Admins assign roles to users from the Users page (modal dialog).

### Payment Proof Upload
- QR payment page (`/qr_payment`) — Drag-and-drop file upload zone.
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

## Important Route Notes
- `admin_edit_product` reads `product_id` from `request.form` (NOT URL) — edit modals need `<input type="hidden" name="product_id">`.
- `profile` route only passes `addresses` to template — no orders_count/reviews_count/tickets_count.
- `change_password` route does NOT exist — do not reference it in templates.
- Support routes: `/support` (centre), `/support/new` (create ticket), `/support/ticket/<id>` (view).

## External Dependencies

### Python Packages
- **Flask, Flask-SQLAlchemy, Werkzeug** — Core framework.
- **pymongo** — MongoDB driver.
- **resend** — Email sending via Resend API.

### Frontend Libraries (CDN)
- Bootstrap 5, Font Awesome 6, Chart.js, Google Fonts (Playfair Display, Poppins, Inter).

### Environment Variables / Secrets
- `DATABASE_URL` — MongoDB Atlas connection string (mongodb+srv://...).
- `RESEND_API_KEY` — Resend API key for email sending.
- `SESSION_SECRET` — Flask session secret key.

### File Storage
- `static/uploads/payment_proofs/` — Payment screenshot uploads.
- `static/images/payment_qr.jpg` — UPI QR code image.
