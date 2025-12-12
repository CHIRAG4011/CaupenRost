# CaupenRost

## Overview
CaupenRost is a Flask-based e-commerce web application for an online bakery, rebranded from "Sweet Crumbs Bakery." It offers a complete shopping experience with product browsing, cart management, order placement, user authentication, and administrative tools. Key features include a bakery-themed design (brown and cream), search and filtering for products, order tracking, user profile management, and comprehensive admin functionalities. The application uses Indian Rupee (INR) for all transactions and features a custom QR code payment system.

## User Preferences
Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Template Engine**: Jinja2 with Flask.
- **CSS Framework**: Bootstrap 5 for responsiveness.
- **Custom Styling**: CSS custom properties for a bakery theme.
- **JavaScript**: Vanilla JS for interactive elements, Chart.js for analytics, Font Awesome for icons.
- **Typography**: Google Fonts (Playfair Display, Poppins, Dancing Script) for a premium look.
- **UI/UX Decisions**: Modernized design with CSS custom properties, gradients, shadows, gold accents, top announcement bar, redesigned hero section with animations, trust strip, enhanced product cards, testimonials, category previews, and an improved footer. Enhanced cart and checkout pages with step indicators and clear payment options.

### Backend Architecture
- **Web Framework**: Flask with modular organization.
- **Session Management**: Flask sessions for cart and authentication.
- **Email System**: Flask-Mail for order confirmations and notifications.
- **Data Models**: Object-oriented models for User, Product, Order, Review, Address, and Category.
- **Authentication**: Werkzeug password hashing, session-based user management, role-based access control.
- **Security**: Configurable session secret key, input validation, and access control.

### Data Storage
- **Dual Database Support**: Supports SQLAlchemy (PostgreSQL/SQLite) and MongoDB.
- **SQLAlchemy Mode**: Default using Flask-SQLAlchemy.
- **MongoDB Mode**: Enabled via `MONGO_URI` environment variable, using separate repository classes.
- **Dynamic Backend Selection**: Conditional imports based on `USE_MONGODB` flag.

### Application Structure
- **Modular Design**: Separated concerns (routes, models, utilities).
- **Admin Interface**: Dedicated templates and routes for management of products, orders, users, and categories.

### Key Features
- **Product Management**: Full CRUD operations for products and categories via admin panel, with dynamic category integration and product filtering.
- **QR Code Payment**: Custom UPI QR code payment system integrated with manual confirmation, alongside Cash on Delivery (COD).
- **Analytics Dashboard**: Chart.js integration for admin analytics.
- **Comprehensive Deployment Guide**: `DEPLOYMENT_GUIDE.md` with instructions for various hosting platforms.

## External Dependencies

### Python Packages
- **Flask**: Core web framework.
- **Flask-Mail**: Email capabilities.
- **Werkzeug**: Password hashing and WSGI.

### Frontend Libraries
- **Bootstrap 5**: CSS framework (via CDN).
- **Font Awesome 6**: Icon library (via CDN).
- **Chart.js**: JavaScript charting library.
- **Intl.NumberFormat**: JavaScript for Indian Rupee formatting (`en-IN` locale).

### Email Service
- **Gmail SMTP**: Used for sending OTP and notification emails, requires Google App Password.

### Database Configuration
- **SQLAlchemy**: Supports PostgreSQL or SQLite.
- **MongoDB**: Option to use MongoDB Atlas.

### Image Resources
- **Unsplash**: External hosting for product photos and promotional imagery.

### Typography
- **Google Fonts**: Playfair Display, Poppins, Dancing Script.