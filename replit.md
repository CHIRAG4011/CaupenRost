# CaupenRost

## Overview

CaupenRost is a Flask-based e-commerce web application for an online bakery business. The application provides a complete shopping experience with product browsing, cart management, order placement, user authentication, and admin management capabilities. It features a warm, bakery-themed design with brown and cream color schemes, product catalogs with search and filtering, shopping cart functionality, order tracking, user profile management, and comprehensive admin tools for managing products, orders, and analytics. The application has been fully rebranded from "Sweet Crumbs Bakery" to "CaupenRost" and converted to use Indian Rupee (INR) currency throughout.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Template Engine**: Jinja2 templates with Flask for server-side rendering
- **CSS Framework**: Bootstrap 5 for responsive design and UI components
- **Custom Styling**: CSS custom properties for consistent bakery theme (brown/cream color palette)
- **JavaScript**: Vanilla JavaScript for cart management and interactive features
- **Icon Library**: Font Awesome for consistent iconography

### Backend Architecture
- **Web Framework**: Flask with modular route organization
- **Session Management**: Flask sessions for cart persistence and user authentication
- **Email System**: Flask-Mail for order confirmations and notifications
- **Data Models**: Object-oriented models for User, Product, Order, Review, and Address entities
- **Authentication**: Werkzeug password hashing with session-based user management
- **Middleware**: ProxyFix for handling reverse proxy headers

### Data Storage
- **Primary Storage**: In-memory data store using Python dictionaries
- **Data Structure**: Hierarchical dictionary structure for users, products, orders, reviews, addresses, and visitor logs
- **Auto-incrementing IDs**: Counter-based ID generation for all entities
- **Session Storage**: Flask sessions for cart data and user authentication state

### Application Structure
- **Modular Design**: Separated concerns with distinct files for routes, models, utilities, and data management
- **Template Hierarchy**: Base template with extending child templates for consistent layout
- **Static Assets**: Organized CSS and JavaScript files for frontend functionality
- **Admin Interface**: Dedicated admin templates and routes for business management

### Security Features
- **Password Security**: Werkzeug password hashing for secure credential storage
- **Session Security**: Configurable session secret key with environment variable support
- **Input Validation**: Form validation and sanitization throughout the application
- **Access Control**: Role-based access with admin user privileges

## External Dependencies

### Python Packages
- **Flask**: Core web framework for routing and request handling
- **Flask-Mail**: Email sending capabilities for order confirmations
- **Werkzeug**: Password hashing and WSGI utilities


### Frontend Libraries
- **Bootstrap 5**: CSS framework loaded via CDN for responsive design
- **Font Awesome 6**: Icon library loaded via CDN for UI elements
- **Chart.js**: JavaScript charting library for admin analytics dashboard
- **Currency Formatting**: JavaScript uses Intl.NumberFormat with en-IN locale for Indian Rupee formatting

### Email Service
- **Gmail SMTP**: Uses Gmail SMTP directly for sending OTP and notification emails
- **Environment Variables**: GMAIL_EMAIL, GMAIL_APP_PASSWORD (requires Google App Password)
- **Email Templates**: OTP verification, order confirmation, and notification emails with CaupenRost branding

### Database Configuration
- **Database**: MongoDB (NoSQL document database)
- **Cloud Option**: MongoDB Atlas (free tier available) - Recommended for production
- **Local Option**: MongoDB Community Edition for local development
- **Connection**: Configure via MONGO_URI environment variable
- **ORM**: Flask-PyMongo for database operations with repository pattern in db.py

### Image Resources
- **Unsplash**: External image hosting for product photos, hero images, and bakery imagery
- **Stock Photos**: Reliable placeholder images for products and promotional content

### Typography
- **Google Fonts**: Playfair Display (headings), Poppins (body), Dancing Script (decorative)
- **Responsive Typography**: Fluid type scale using CSS clamp() for optimal readability

### Development Tools
- **Environment Configuration**: Development vs production settings via environment variables
- **Debug Mode**: Flask debug mode for development with hot reloading
- **Logging**: Python logging module for application monitoring and debugging

## Recent Changes (August 2025)

### Complete Rebranding and Currency Conversion
- **Business Name**: Changed from "Sweet Crumbs Bakery" to "CaupenRost" across all templates, JavaScript files, and email content
- **Currency Conversion**: Full conversion from USD ($) to Indian Rupee (₹) throughout the application
- **Product Pricing**: Updated all product prices to appropriate INR values (multiplied by ~10x for realistic Indian pricing)
- **Delivery Fees**: Updated from $5.00 to ₹50.00, free delivery threshold changed from $50 to ₹500
- **Tax Rates**: Updated from 8.5% US tax to 18% Indian GST rate
- **Admin Email**: Changed from admin@sweetcrumbsbakery.com to admin@caupenrost.com
- **JavaScript Localization**: Updated currency formatting to use en-IN locale with INR currency
- **Template Fixes**: Fixed analytics template slicing and undefined variable errors

### Major Database Architecture Conversion (August 8, 2025)
- **Database Migration**: Successfully converted from PostgreSQL/SQLAlchemy to in-memory data storage using data_store.py
- **Model Updates**: Updated all data models (User, Product, Order, Review, Address) to work with in-memory storage
- **Route Fixes**: Systematically updated all 40+ routes to use data_store instead of SQLAlchemy queries
- **Error Resolution**: Reduced LSP diagnostics from 40+ critical errors to just 1 false positive
- **Template Context**: Added data_store to template context to fix undefined variable errors
- **Cart Functionality**: Fixed cart clearing after order placement
- **Admin Panel**: Fixed order details display and user management in admin dashboard

### Enhanced Product Management (August 8, 2025)
- **Full Product Customization**: Added complete product editing functionality with modal interface
- **Admin Product Editor**: Implemented edit product modal with all fields (name, description, price, category, image, stock)
- **Validation**: Added proper form validation and user feedback for product operations
- **Required Address**: Made address field required during checkout with proper validation
- **Price Display**: Updated all admin panels to show prices in INR (₹) format

### JavaScript and User Experience Fixes (August 8, 2025)
- **Error Resolution**: Fixed JavaScript errors including missing handleDropdownToggle and initializeCharts functions
- **Chart Integration**: Added proper Chart.js integration for admin analytics dashboard
- **Bootstrap Compatibility**: Fixed dropdown functionality to work with Bootstrap 5
- **Modal Enhancements**: Enhanced product edit modal with proper data binding and validation
- **User Feedback**: Improved form submission feedback and error handling throughout the application

### Analytics and JSON Serialization Fixes (August 8, 2025)
- **Analytics Page Fix**: Resolved JSON serialization error with Order objects in analytics charts
- **Chart Data**: Updated analytics page to properly serialize order data for JavaScript charts
- **Template Fixes**: Fixed remaining Jinja2 template syntax issues throughout the application

### Cart and Order Management Fix (August 8, 2025)
- **Order Placement Issue Resolution**: Fixed critical bug where orders weren't being created due to strict address validation
- **Cart Clearing Fix**: Resolved issue where shopping cart wasn't being cleared after successful order placement
- **Address Validation Enhancement**: Added proper form validation requiring delivery address before order placement
- **JavaScript Validation**: Implemented client-side address validation with user-friendly error messages
- **Order Display Fix**: Confirmed orders now properly appear in user's "My Orders" page after placement

### Complete Currency Conversion to INR (August 8, 2025)
- **Template Currency Update**: Replaced all remaining dollar ($) symbols with Indian Rupee (₹) symbols across all templates
- **JavaScript Currency Fix**: Updated cart.js to properly handle INR currency formatting and calculations
- **Admin Dashboard Currency**: Changed revenue display icons from dollar-sign to rupee-sign in admin analytics
- **Price Display Consistency**: Ensured all product prices, order totals, and financial displays use INR consistently
- **Cart Functionality**: Fixed cart total calculations to properly work with INR currency symbols

### Product Category System Implementation (August 9, 2025)
- **Category Model**: Added comprehensive Category model with description, image, and active status fields
- **Admin Category Management**: Implemented full CRUD operations including add, edit, delete, and toggle active status
- **Customer Category Pages**: Created attractive category browsing and individual category product pages
- **Dynamic Category Integration**: Updated product forms to use database categories instead of hardcoded options
- **Navigation Enhancement**: Added Categories link to main navigation menu
- **Admin Dashboard Integration**: Added category management access to admin quick actions
- **Product Filtering**: Enhanced product filtering to work with dynamic database categories
- **Delete Functionality**: Added delete capabilities for both categories and products with safety checks
- **Data Integrity**: Categories with products cannot be deleted; product deletion removes associated reviews

### QR Code Payment Integration (August 9, 2025)
- **Custom Payment Gateway**: Replaced third-party payment gateway with custom QR code payment system
- **UPI QR Code**: Integrated personal UPI QR code (7016377439@fam) for direct payments
- **Payment Methods**: Support for QR code payments via any UPI app (Google Pay, PhonePe, Paytm, etc.)
- **Cash on Delivery**: Maintained COD option with ₹20 handling charges
- **Order Flow**: Enhanced order creation with payment status tracking (payment_pending → confirmed)
- **QR Payment Page**: Dedicated payment page displaying QR code with clear instructions
- **Payment Confirmation**: Manual payment confirmation system with order status updates
- **User Experience**: Simple scan-and-pay interface with step-by-step instructions
- **Mobile Optimized**: QR code optimized for mobile scanning and payment
- **Payment Tracking**: Order status updates based on payment confirmation

### Deployment Documentation (August 8, 2025)
- **Comprehensive Deployment Guide**: Created extensive DEPLOYMENT_GUIDE.md with 890+ lines covering local and free hosting
- **Multiple Platform Support**: Detailed instructions for 6 hosting platforms (Replit, Railway, Render, Fly.io, Vercel, PythonAnywhere)
- **Local Development**: 3 different setup methods with step-by-step instructions for beginners and developers
- **Configuration Files**: Complete set including Procfile, runtime.txt, .env.example, app.json, Dockerfile, and .dockerignore
- **Production Considerations**: Security headers, database options, email services, performance optimization, and scaling
- **Troubleshooting Guide**: Comprehensive troubleshooting covering local development, deployment issues, and platform-specific problems
- **Quick Start Summary**: Easy-to-follow deployment instructions for different skill levels and hosting preferences

### Major UI/UX Enhancement (December 2025)
- **Complete CSS Overhaul**: Modernized design system with CSS custom properties, gradients, and shadows
- **Typography Upgrade**: Integrated Google Fonts (Playfair Display, Poppins, Dancing Script) for premium look
- **Color Palette Enhancement**: Added gold accents, refined brown tones, and cream gradients
- **Top Announcement Bar**: Added contact info, delivery promotions, and trust badges
- **Enhanced Navigation**: Scroll-responsive navbar with active states, hover effects, and improved mobile menu
- **Redesigned Hero Section**: Full-height hero with floating cards, animations, badge, and improved CTA buttons
- **Trust Strip Section**: Added trust indicators below hero (Fresh Daily, Fast Delivery, Easy Payment, Made with Love)
- **Enhanced Feature Cards**: Improved icons with gradient backgrounds and hover animations
- **Product Card Redesign**: Quick action buttons, category badges, ratings display, hover overlays, and stock status
- **Testimonials Section**: Customer reviews with avatars, ratings, and animated cards
- **Category Preview Section**: Visual category cards with overlay text and hover effects
- **CTA Section**: Gradient background with call-to-action for ordering
- **Footer Enhancement**: Social media links, newsletter signup, payment badges, and improved layout
- **Cart Page Improvements**: Better layout, quantity controls with +/- buttons, trust badges, and free delivery indicator
- **Checkout Page Redesign**: Step indicators, enhanced payment method selection, QR/COD options with clear details
- **Product Detail Page**: Interactive rating stars, enhanced layout, product benefits section
- **Micro-interactions**: Smooth hover effects, reveal-on-scroll animations, toast notifications
- **Mobile Responsiveness**: Improved breakpoints and mobile-first design considerations
- **Image Migration**: Updated all images from Pixabay to Unsplash for reliable loading

