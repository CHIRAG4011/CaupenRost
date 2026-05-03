from flask import render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from app import app, USE_MONGODB
import logging
from datetime import datetime

if USE_MONGODB:
    from mongo_db import (MongoUserRepo as UserRepo, MongoProductRepo as ProductRepo, 
                         MongoOrderRepo as OrderRepo, MongoCategoryRepo as CategoryRepo, 
                         MongoReviewRepo as ReviewRepo, MongoAddressRepo as AddressRepo, 
                         MongoVisitorLogRepo as VisitorLogRepo,
                         MongoTicketRepo as TicketRepo, MongoTicketMessageRepo as TicketMessageRepo,
                         MongoRoleRepo as RoleRepo,
                         MongoAnnouncementRepo as AnnouncementRepo,
                         MongoCouponRepo as CouponRepo)
else:
    from db import (UserRepo, ProductRepo, OrderRepo, CategoryRepo, ReviewRepo, 
                    AddressRepo, VisitorLogRepo, TicketRepo, TicketMessageRepo)
    RoleRepo = None
    AnnouncementRepo = None
    CouponRepo = None

from data_store import add_visitor_log, get_weekly_visitors
from utils import (get_current_user, add_to_cart, remove_from_cart, update_cart_quantity,
                  get_cart_total, get_cart_count, clear_cart,
                  calculate_order_stats, search_products, get_cart)
from email_service import (send_and_store_otp, verify_otp,
                           send_welcome_email, send_welcome_back_email,
                           send_order_confirmation_email, send_order_status_email)

@app.before_request
def log_visitor():
    """Log visitor information"""
    if request.endpoint not in ['static']:
        try:
            add_visitor_log(
                request.remote_addr,
                request.headers.get('User-Agent', ''),
                request.endpoint
            )
        except Exception as e:
            logging.warning(f"Failed to log visitor: {e}")

@app.context_processor
def inject_globals():
    """Inject global variables into templates"""
    try:
        current_user = get_current_user()
    except Exception:
        current_user = None
    return {
        'current_user': current_user,
        'cart_count': get_cart_count(),
        'cart_total': get_cart_total()
    }

@app.route('/')
def index():
    """Home page"""
    featured_products = ProductRepo.find_limit(6)
    real_reviews = []
    try:
        if USE_MONGODB:
            real_reviews = ReviewRepo.find_top_rated(min_rating=4, limit=5)
    except Exception:
        real_reviews = []
    return render_template('index.html', featured_products=featured_products, real_reviews=real_reviews)

@app.route('/products')
def products():
    """Products page with search and filter"""
    query = request.args.get('q', '')
    category = request.args.get('category', 'all')
    
    if query or category != 'all':
        product_list = search_products(query, category)
    else:
        product_list = ProductRepo.find_all()
    
    categories = [cat.name for cat in CategoryRepo.find_active()]
    
    return render_template('products.html', 
                         products=product_list, 
                         categories=categories,
                         current_query=query,
                         current_category=category)

@app.route('/categories')
def categories():
    """Categories page showing all available categories"""
    active_categories = CategoryRepo.find_active()
    return render_template('categories.html', categories=active_categories)

@app.route('/category/<category_name>')
def category_products(category_name):
    """Show products for a specific category"""
    category = CategoryRepo.find_by_name(category_name)
    
    if not category or not category.is_active:
        flash('Category not found.', 'error')
        return redirect(url_for('products'))
    
    category_products_list = ProductRepo.find_by_category(category_name)
    
    return render_template('category_products.html', 
                         category=category, 
                         products=category_products_list)

@app.route('/product/<product_id>')
def product_detail(product_id):
    """Product detail page"""
    product = ProductRepo.find_by_id(product_id)
    if not product:
        from flask import abort
        abort(404)
    
    product_reviews = ReviewRepo.find_by_product(product_id)
    
    return render_template('product_detail.html', product=product, reviews=product_reviews)

@app.route('/add_to_cart/<product_id>', methods=['POST'])
def add_to_cart_route(product_id):
    """Add item to cart"""
    quantity = int(request.form.get('quantity', 1))
    
    if add_to_cart(product_id, quantity):
        flash('Item added to cart!', 'success')
    else:
        flash('Unable to add item to cart. Please check availability.', 'error')
    
    return redirect(request.referrer or url_for('products'))

@app.route('/cart')
def cart():
    """Shopping cart page"""
    cart_items = []
    cart_data = get_cart()
    
    for product_id_str, item_data in cart_data.items():
        product = ProductRepo.find_by_id(product_id_str)
        if product:
            cart_items.append({
                'product': product,
                'quantity': item_data['quantity'],
                'total': item_data['quantity'] * item_data['price']
            })
    
    return render_template('cart.html', cart_items=cart_items)

@app.route('/update_cart', methods=['POST'])
def update_cart():
    """Update cart quantities"""
    product_id = request.form.get('product_id', '0')
    quantity = int(request.form.get('quantity', '1'))
    
    if update_cart_quantity(product_id, quantity):
        flash('Cart updated!', 'success')
    else:
        flash('Unable to update cart.', 'error')
    
    return redirect(url_for('cart'))

@app.route('/remove_from_cart/<product_id>')
def remove_from_cart_route(product_id):
    """Remove item from cart"""
    if remove_from_cart(product_id):
        flash('Item removed from cart!', 'success')
    else:
        flash('Unable to remove item.', 'error')
    
    return redirect(url_for('cart'))

@app.route('/checkout')
def checkout():
    """Checkout page"""
    user = get_current_user()
    if not user:
        flash('Please login to checkout.', 'error')
        return redirect(url_for('login'))
    
    cart_data = get_cart()
    if not cart_data:
        flash('Your cart is empty.', 'error')
        return redirect(url_for('cart'))
    
    user_addresses = AddressRepo.find_by_user(user.id)
    
    cart_total = get_cart_total()
    delivery_fee = 50.00
    tax_amount = (cart_total + delivery_fee) * 0.18
    final_amount = cart_total + delivery_fee + tax_amount
    
    return render_template('checkout.html', 
                         addresses=user_addresses,
                         final_amount=final_amount)

@app.route('/place_order', methods=['POST'])
def place_order():
    """Process order placement - Step 1: Validate and send OTP"""
    user = get_current_user()
    if not user:
        flash('Please login to place an order.', 'error')
        return redirect(url_for('login'))
    
    cart_data = get_cart()
    if not cart_data:
        flash('Your cart is empty.', 'error')
        return redirect(url_for('cart'))
    
    address_id = request.form.get('address_id')
    new_address = request.form.get('new_address')
    payment_method = request.form.get('payment_method', 'qr_payment')
    
    if address_id:
        address = AddressRepo.find_by_id(address_id)
        if address:
            shipping_address = f"{address.name}, {address.street}, {address.city}, {address.state} {address.zip_code}"
        else:
            flash('Selected address not found.', 'error')
            return redirect(url_for('checkout'))
    elif new_address and new_address.strip():
        shipping_address = new_address.strip()
    else:
        flash('Please provide a delivery address to continue.', 'error')
        return redirect(url_for('checkout'))
    
    cart_total = get_cart_total()
    delivery_fee = 0.00 if cart_total >= 500 else 50.00
    tax_amount = (cart_total + delivery_fee) * 0.18

    # Apply coupon discount if any
    coupon_code = session.get('applied_coupon_code')
    coupon_discount = float(session.get('applied_coupon_discount', 0))
    if coupon_code and CouponRepo:
        coupon = CouponRepo.find_by_code(coupon_code)
        if coupon:
            valid, _ = coupon.is_valid(cart_total)
            if valid:
                coupon_discount = coupon.calculate_discount(cart_total)
            else:
                coupon_discount = 0
                session.pop('applied_coupon_code', None)
                session.pop('applied_coupon_discount', None)

    final_amount = cart_total + delivery_fee + tax_amount - coupon_discount
    if payment_method == 'cash_on_delivery':
        final_amount += 20.00
    final_amount = max(final_amount, 1.0)
    
    for product_id_str, item_data in cart_data.items():
        product = ProductRepo.find_by_id(product_id_str)
        
        if not product or product.stock < item_data['quantity']:
            flash(f'Insufficient stock for {product.name if product else "unknown item"}.', 'error')
            return redirect(url_for('cart'))
    
    session['pending_order'] = {
        'shipping_address': shipping_address,
        'payment_method': payment_method,
        'final_amount': final_amount,
        'coupon_code': coupon_code if coupon_discount > 0 else None,
        'coupon_discount': coupon_discount
    }
    
    if send_and_store_otp(user.email, 'order'):
        flash('A verification code has been sent to your email to confirm your order.', 'success')
        return redirect(url_for('verify_order_otp'))
    else:
        flash('Failed to send verification email. Please try again.', 'error')
        return redirect(url_for('checkout'))


@app.route('/verify-order', methods=['GET', 'POST'])
def verify_order_otp():
    """Order placement - Step 2: Verify OTP and create order"""
    user = get_current_user()
    if not user:
        flash('Please login to place an order.', 'error')
        return redirect(url_for('login'))
    
    pending = session.get('pending_order')
    if not pending:
        flash('Please start the checkout process.', 'error')
        return redirect(url_for('checkout'))
    
    cart_data = get_cart()
    if not cart_data:
        flash('Your cart is empty.', 'error')
        session.pop('pending_order', None)
        return redirect(url_for('cart'))
    
    if request.method == 'POST':
        otp = request.form.get('otp', '').strip()
        
        if not otp:
            flash('Please enter the verification code.', 'error')
            return render_template('auth/verify_otp.html', purpose='order', email=user.email, amount=pending['final_amount'])
        
        success, message = verify_otp(user.email, otp, 'order')
        
        if success:
            if pending['payment_method'] == 'cash_on_delivery':
                status = 'pending'
            else:
                status = 'payment_pending'
            
            order_items = []
            for product_id_str, item_data in cart_data.items():
                product = ProductRepo.find_by_id(product_id_str)
                
                if not product or product.stock < item_data['quantity']:
                    flash(f'Insufficient stock for {product.name if product else "unknown item"}.', 'error')
                    session.pop('pending_order', None)
                    return redirect(url_for('cart'))
                
                order_items.append({
                    'product_id': product_id_str,
                    'quantity': item_data['quantity'],
                    'price': item_data['price']
                })
                
                ProductRepo.update(product_id_str, {'stock': product.stock - item_data['quantity']})
            
            order = OrderRepo.create({
                'user_id': user.id,
                'total': pending['final_amount'],
                'shipping_address': pending['shipping_address'],
                'status': status,
                'payment_method': pending['payment_method'],
                'items': order_items,
                'coupon_code': pending.get('coupon_code'),
                'coupon_discount': pending.get('coupon_discount', 0)
            })

            # Track coupon usage
            if pending.get('coupon_code') and CouponRepo:
                coupon = CouponRepo.find_by_code(pending['coupon_code'])
                if coupon:
                    CouponRepo.increment_uses(coupon.id)

            try:
                send_order_confirmation_email(user.email, order)
            except Exception as e:
                logging.warning(f"Failed to send confirmation email: {e}")

            clear_cart()
            session.pop('pending_order', None)
            session.pop('applied_coupon_code', None)
            session.pop('applied_coupon_discount', None)
            
            if pending['payment_method'] == 'cash_on_delivery':
                flash(f'Order #{order.id} placed successfully! Payment will be collected on delivery.', 'success')
                return redirect(url_for('order_tracking', order_id=order.id))
            else:
                session['payment_order_id'] = order.id
                session['payment_amount'] = pending['final_amount']
                return redirect(url_for('qr_payment'))
        else:
            flash(message, 'error')
    
    return render_template('auth/verify_otp.html', purpose='order', email=user.email, amount=pending['final_amount'])


@app.route('/resend-order-otp', methods=['POST'])
def resend_order_otp():
    """Resend order confirmation OTP"""
    user = get_current_user()
    if not user:
        flash('Please login to place an order.', 'error')
        return redirect(url_for('login'))
    
    pending = session.get('pending_order')
    if not pending:
        flash('Please start the checkout process.', 'error')
        return redirect(url_for('checkout'))
    
    if send_and_store_otp(user.email, 'order'):
        flash('A new verification code has been sent.', 'success')
    else:
        flash('Failed to resend verification code. Please try again.', 'error')
    
    return redirect(url_for('verify_order_otp'))

@app.route('/qr_payment')
def qr_payment():
    """QR code payment page"""
    user = get_current_user()
    if not user:
        flash('Please login to continue.', 'error')
        return redirect(url_for('login'))
    
    order_id = session.get('payment_order_id')
    amount = session.get('payment_amount')
    
    if not order_id or not amount:
        flash('Invalid payment session.', 'error')
        return redirect(url_for('index'))
    
    order = OrderRepo.find_by_id(order_id)
    if not order:
        flash('Order not found.', 'error')
        return redirect(url_for('index'))
    
    return render_template('qr_payment.html', 
                         order_id=order_id, 
                         amount=amount,
                         order=order)

@app.route('/confirm_payment/<order_id>', methods=['POST'])
def confirm_payment(order_id):
    """Confirm QR code payment"""
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Please login to proceed'}), 401
    
    order = OrderRepo.find_by_id(order_id)
    if not order or order.user_id != user.id:
        return jsonify({'error': 'Order not found'}), 404
    
    OrderRepo.update(order_id, {'status': 'confirmed'})
    
    session.pop('payment_order_id', None)
    session.pop('payment_amount', None)
    
    flash(f'Payment confirmed! Order #{order_id} is now being processed.', 'success')
    return jsonify({'success': True, 'redirect': url_for('order_tracking', order_id=order_id)})

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration - Step 1: Collect details and send OTP"""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if not all([username, email, password, confirm_password]):
            flash('All fields are required.', 'error')
            return render_template('auth/register.html')
        
        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return render_template('auth/register.html')
        
        password_errors = []
        if len(password) < 8:
            password_errors.append('at least 8 characters')
        if not any(c.isupper() for c in password):
            password_errors.append('one uppercase letter')
        if not any(c.islower() for c in password):
            password_errors.append('one lowercase letter')
        if not any(c.isdigit() for c in password):
            password_errors.append('one number')
        if not any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password):
            password_errors.append('one special character (!@#$%^&*)')
        
        if password_errors:
            flash(f'Password must contain: {", ".join(password_errors)}.', 'error')
            return render_template('auth/register.html')
        
        if UserRepo.exists_by_username_or_email(username, email):
            flash('Username or email already exists.', 'error')
            return render_template('auth/register.html')
        
        session['pending_registration'] = {
            'username': username,
            'email': email,
            'password': password
        }
        
        if send_and_store_otp(email, 'registration'):
            flash('A verification code has been sent to your email.', 'success')
            return redirect(url_for('verify_registration_otp'))
        else:
            flash('Failed to send verification email. Please try again.', 'error')
            return render_template('auth/register.html')
    
    return render_template('auth/register.html')


@app.route('/verify-registration', methods=['GET', 'POST'])
def verify_registration_otp():
    """User registration - Step 2: Verify OTP"""
    pending = session.get('pending_registration')
    if not pending:
        flash('Please start the registration process.', 'error')
        return redirect(url_for('register'))
    
    if request.method == 'POST':
        otp = request.form.get('otp', '').strip()
        
        if not otp:
            flash('Please enter the verification code.', 'error')
            return render_template('auth/verify_otp.html', purpose='registration', email=pending['email'])
        
        success, message = verify_otp(pending['email'], otp, 'registration')
        
        if success:
            user = UserRepo.create({
                'username': pending['username'],
                'email': pending['email'],
                'password_hash': generate_password_hash(pending['password'] or ''),
                'is_admin': False
            })

            try:
                send_welcome_email(pending['email'], pending['username'])
            except Exception as e:
                logging.warning(f"Failed to send welcome email: {e}")

            session.pop('pending_registration', None)
            flash('Email verified! Registration successful. Please login.', 'success')
            return redirect(url_for('login'))
        else:
            flash(message, 'error')
    
    return render_template('auth/verify_otp.html', purpose='registration', email=pending['email'])


@app.route('/resend-registration-otp', methods=['POST'])
def resend_registration_otp():
    """Resend registration OTP"""
    pending = session.get('pending_registration')
    if not pending:
        flash('Please start the registration process.', 'error')
        return redirect(url_for('register'))
    
    if send_and_store_otp(pending['email'], 'registration'):
        flash('A new verification code has been sent.', 'success')
    else:
        flash('Failed to resend verification code. Please try again.', 'error')
    
    return redirect(url_for('verify_registration_otp'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login - Step 1: Validate credentials and send OTP"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = UserRepo.find_by_username_or_email(username)
        
        if user and user.check_password(password):
            session['pending_login'] = {
                'user_id': user.id,
                'email': user.email,
                'next': request.args.get('next')
            }
            
            if send_and_store_otp(user.email, 'login'):
                flash('A verification code has been sent to your email.', 'success')
                return redirect(url_for('verify_login_otp'))
            else:
                flash('Failed to send verification email. Please try again.', 'error')
        else:
            flash('Invalid username/email or password.', 'error')
    
    return render_template('auth/login.html')


@app.route('/verify-login', methods=['GET', 'POST'])
def verify_login_otp():
    """User login - Step 2: Verify OTP"""
    pending = session.get('pending_login')
    if not pending:
        flash('Please login first.', 'error')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        otp = request.form.get('otp', '').strip()
        
        if not otp:
            flash('Please enter the verification code.', 'error')
            return render_template('auth/verify_otp.html', purpose='login', email=pending['email'])
        
        success, message = verify_otp(pending['email'], otp, 'login')

        if success:
            session['user_id'] = pending['user_id']
            next_page = pending.get('next')
            session.pop('pending_login', None)
            flash('Login successful!', 'success')
            try:
                logged_in_user = UserRepo.find_by_id(pending['user_id'])
                if logged_in_user:
                    send_welcome_back_email(logged_in_user.email, logged_in_user.username)
            except Exception as e:
                logging.warning(f"Failed to send welcome-back email: {e}")
            return redirect(next_page or url_for('index'))
        else:
            flash(message, 'error')
    
    return render_template('auth/verify_otp.html', purpose='login', email=pending['email'])


@app.route('/resend-login-otp', methods=['POST'])
def resend_login_otp():
    """Resend login OTP"""
    pending = session.get('pending_login')
    if not pending:
        flash('Please login first.', 'error')
        return redirect(url_for('login'))
    
    if send_and_store_otp(pending['email'], 'login'):
        flash('A new verification code has been sent.', 'success')
    else:
        flash('Failed to resend verification code. Please try again.', 'error')
    
    return redirect(url_for('verify_login_otp'))

@app.route('/logout')
def logout():
    """User logout"""
    session.pop('user_id', None)
    session.pop('cart', None)
    flash('Logged out successfully.', 'success')
    return redirect(url_for('index'))

@app.route('/profile')
def profile():
    """User profile page"""
    user = get_current_user()
    if not user:
        flash('Please login to view your profile.', 'error')
        return redirect(url_for('login'))
    
    user_addresses = AddressRepo.find_by_user(user.id)
    
    return render_template('user/profile.html', addresses=user_addresses)

@app.route('/add_address', methods=['POST'])
def add_address():
    """Add a new address"""
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))
    
    AddressRepo.create({
        'user_id': user.id,
        'name': request.form.get('name'),
        'street': request.form.get('street'),
        'city': request.form.get('city'),
        'state': request.form.get('state'),
        'zip_code': request.form.get('zip_code')
    })
    
    flash('Address added successfully!', 'success')
    return redirect(url_for('profile'))

@app.route('/orders')
def user_orders():
    """User orders page"""
    user = get_current_user()
    if not user:
        flash('Please login to view your orders.', 'error')
        return redirect(url_for('login'))
    
    user_orders_list = OrderRepo.find_by_user(user.id)
    
    return render_template('user/orders.html', orders=user_orders_list)

@app.route('/order/<order_id>')
def order_tracking(order_id):
    """Order tracking page"""
    order = OrderRepo.find_by_id(order_id)
    if not order:
        flash('Order not found.', 'error')
        return redirect(url_for('user_orders'))
    
    user = get_current_user()
    if not user or (order.user_id != user.id and not user.is_admin):
        flash('Unauthorized access.', 'error')
        return redirect(url_for('index'))
    
    order_items = []
    for item in order.items:
        if isinstance(item, dict):
            product_id = item.get('product_id')
            quantity = item.get('quantity', 1)
            price = item.get('price', 0)
        else:
            product_id = getattr(item, 'product_id', None)
            quantity = getattr(item, 'quantity', 1)
            price = getattr(item, 'price', 0)
        
        product = ProductRepo.find_by_id(product_id)
        if product:
            order_items.append({
                'product': product,
                'quantity': quantity,
                'price': price,
                'total': quantity * price
            })
    
    return render_template('user/order_detail.html', order=order, order_items=order_items)

@app.route('/add_review/<product_id>', methods=['POST'])
def add_review(product_id):
    """Add a product review"""
    user = get_current_user()
    if not user:
        flash('Please login to add a review.', 'error')
        return redirect(url_for('login'))
    
    rating = int(request.form.get('rating', '1'))
    comment = request.form.get('comment')
    
    ReviewRepo.create({
        'product_id': product_id,
        'user_id': user.id,
        'rating': rating,
        'comment': comment
    })
    
    flash('Review added successfully!', 'success')
    return redirect(url_for('product_detail', product_id=product_id))

@app.route('/admin')
def admin_dashboard():
    """Admin dashboard"""
    user = get_current_user()
    if not user or not user.is_admin:
        flash('Access denied.', 'error')
        return redirect(url_for('index'))
    
    stats = calculate_order_stats()
    from data_store import get_daily_visitors
    daily_visitors = get_daily_visitors()
    recent_orders = OrderRepo.find_recent(10)
    
    return render_template('admin/dashboard.html', 
                         stats=stats, 
                         daily_visitors=daily_visitors,
                         recent_orders=recent_orders)

@app.route('/admin/products')
def admin_products():
    """Admin products management"""
    user = get_current_user()
    if not user or not user.is_admin:
        flash('Access denied.', 'error')
        return redirect(url_for('index'))
    
    products = ProductRepo.find_all()
    categories = CategoryRepo.find_all()
    return render_template('admin/products.html', products=products, categories=categories)

@app.route('/admin/add_product', methods=['POST'])
def admin_add_product():
    """Add a new product"""
    user = get_current_user()
    if not user or not user.is_admin:
        return redirect(url_for('index'))
    
    category_name = request.form.get('category')
    cat = CategoryRepo.find_by_name(category_name)
    
    ProductRepo.create({
        'name': request.form.get('name'),
        'description': request.form.get('description'),
        'price': float(request.form.get('price', '0')),
        'category': category_name,
        'category_id': cat.id if cat else None,
        'image_url': request.form.get('image_url'),
        'stock': int(request.form.get('stock', '0'))
    })
    
    flash('Product added successfully!', 'success')
    return redirect(url_for('admin_products'))

@app.route('/admin/update_stock/<product_id>', methods=['POST'])
def admin_update_stock(product_id):
    """Update product stock"""
    user = get_current_user()
    if not user or not user.is_admin:
        return redirect(url_for('index'))
    
    product = ProductRepo.find_by_id(product_id)
    if product:
        ProductRepo.update(product_id, {'stock': int(request.form.get('stock', '0'))})
        flash('Stock updated successfully!', 'success')
    
    return redirect(url_for('admin_products'))

@app.route('/admin/edit_product', methods=['POST'])
def admin_edit_product():
    """Edit an existing product"""
    user = get_current_user()
    if not user or not user.is_admin:
        return redirect(url_for('index'))
    
    product_id = request.form.get('product_id')
    if not product_id:
        flash('Product ID is required.', 'error')
        return redirect(url_for('admin_products'))
    
    product = ProductRepo.find_by_id(product_id)
    
    if product:
        category_name = request.form.get('category')
        cat = CategoryRepo.find_by_name(category_name)
        
        ProductRepo.update(product_id, {
            'name': request.form.get('name'),
            'description': request.form.get('description'),
            'price': float(request.form.get('price', '0')),
            'category': category_name,
            'category_id': cat.id if cat else None,
            'image_url': request.form.get('image_url'),
            'stock': int(request.form.get('stock', '0'))
        })
        flash('Product updated successfully!', 'success')
    
    return redirect(url_for('admin_products'))

@app.route('/admin/orders')
def admin_orders():
    """Admin orders management"""
    user = get_current_user()
    if not user or not user.is_admin:
        flash('Access denied.', 'error')
        return redirect(url_for('index'))
    
    orders = OrderRepo.find_all()
    
    return render_template('admin/orders.html', orders=orders)

@app.route('/admin/update_order_status/<order_id>', methods=['POST'])
def admin_update_order_status(order_id):
    """Update order status"""
    user = get_current_user()
    if not user or not user.is_admin:
        return redirect(url_for('index'))
    
    order = OrderRepo.find_by_id(order_id)
    if order:
        new_status = request.form.get('status')
        OrderRepo.update(order_id, {'status': new_status})
        order.status = new_status
        flash('Order status updated successfully!', 'success')
        try:
            customer = UserRepo.find_by_id(order.user_id)
            if customer:
                send_order_status_email(customer.email, customer.username, order)
        except Exception as e:
            logging.warning(f"Failed to send order status email: {e}")

    return redirect(url_for('admin_orders'))

@app.route('/admin/analytics')
def admin_analytics():
    """Admin analytics page"""
    user = get_current_user()
    if not user or not user.is_admin:
        flash('Access denied.', 'error')
        return redirect(url_for('index'))
    
    weekly_visitors = get_weekly_visitors()
    stats = calculate_order_stats()
    products = ProductRepo.find_all()
    orders = OrderRepo.find_all()
    users_count = UserRepo.count()
    reviews_count = ReviewRepo.count()
    addresses_count = AddressRepo.count()
    
    return render_template('admin/analytics.html', 
                         weekly_visitors=weekly_visitors,
                         stats=stats,
                         products=products,
                         orders=orders,
                         users_count=users_count,
                         reviews_count=reviews_count,
                         addresses_count=addresses_count)

@app.route('/admin/users')
def admin_users():
    """Admin user management"""
    user = get_current_user()
    if not user or not user.is_admin:
        flash('Access denied.', 'error')
        return redirect(url_for('index'))
    
    users = UserRepo.find_all()
    return render_template('admin/users.html', users=users, current_user=user)

@app.route('/admin/categories')
def admin_categories():
    """Admin category management"""
    user = get_current_user()
    if not user or not user.is_admin:
        flash('Access denied.', 'error')
        return redirect(url_for('index'))
    
    categories = CategoryRepo.find_all()
    return render_template('admin/categories.html', categories=categories)

@app.route('/admin/add_category', methods=['GET', 'POST'])
def admin_add_category():
    """Add new category"""
    user = get_current_user()
    if not user or not user.is_admin:
        flash('Access denied.', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        image_url = request.form.get('image_url', '').strip()
        
        if not name:
            flash('Category name is required.', 'error')
            return render_template('admin/add_category.html')
        
        if CategoryRepo.exists_by_name_exclude(name, None):
            flash('Category with this name already exists.', 'error')
            return render_template('admin/add_category.html')
        
        CategoryRepo.create({
            'name': name,
            'description': description,
            'image_url': image_url
        })
        
        flash(f'Category "{name}" added successfully!', 'success')
        return redirect(url_for('admin_categories'))
    
    return render_template('admin/add_category.html')

@app.route('/admin/edit_category/<category_id>', methods=['GET', 'POST'])
def admin_edit_category(category_id):
    """Edit existing category"""
    user = get_current_user()
    if not user or not user.is_admin:
        flash('Access denied.', 'error')
        return redirect(url_for('index'))
    
    category = CategoryRepo.find_by_id(category_id)
    if not category:
        flash('Category not found.', 'error')
        return redirect(url_for('admin_categories'))
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        image_url = request.form.get('image_url', '').strip()
        is_active = request.form.get('is_active') == 'on'
        
        if not name:
            flash('Category name is required.', 'error')
            return render_template('admin/edit_category.html', category=category)
        
        if CategoryRepo.exists_by_name_exclude(name, category_id):
            flash('Category with this name already exists.', 'error')
            return render_template('admin/edit_category.html', category=category)
        
        CategoryRepo.update(category_id, {
            'name': name,
            'description': description,
            'image_url': image_url,
            'is_active': is_active
        })
        
        flash(f'Category "{name}" updated successfully!', 'success')
        return redirect(url_for('admin_categories'))
    
    return render_template('admin/edit_category.html', category=category)

@app.route('/admin/toggle_category_status/<category_id>', methods=['POST'])
def admin_toggle_category_status(category_id):
    """Toggle category active status"""
    user = get_current_user()
    if not user or not user.is_admin:
        flash('Access denied.', 'error')
        return redirect(url_for('index'))
    
    category = CategoryRepo.find_by_id(category_id)
    if not category:
        flash('Category not found.', 'error')
        return redirect(url_for('admin_categories'))
    
    CategoryRepo.update(category_id, {'is_active': not category.is_active})
    status = "activated" if not category.is_active else "deactivated"
    flash(f'Category "{category.name}" {status} successfully!', 'success')
    
    return redirect(url_for('admin_categories'))

@app.route('/admin/delete_category/<category_id>', methods=['POST', 'GET'])
def admin_delete_category(category_id):
    """Delete a category"""
    user = get_current_user()
    if not user or not user.is_admin:
        flash('Access denied.', 'error')
        return redirect(url_for('index'))
    
    category = CategoryRepo.find_by_id(category_id)
    if not category:
        flash('Category not found.', 'error')
        return redirect(url_for('admin_categories'))
    
    products_in_category = ProductRepo.find_by_category(category.name)
    if products_in_category:
        flash(f'Cannot delete category "{category.name}" because it contains {len(products_in_category)} products. Please move or delete these products first.', 'error')
        return redirect(url_for('admin_categories'))
    
    category_name = category.name
    CategoryRepo.delete(category_id)
    flash(f'Category "{category_name}" deleted successfully!', 'success')
    
    return redirect(url_for('admin_categories'))

@app.route('/admin/delete_product/<product_id>', methods=['POST'])
def admin_delete_product(product_id):
    """Delete a product"""
    user = get_current_user()
    if not user or not user.is_admin:
        flash('Access denied.', 'error')
        return redirect(url_for('index'))
    
    product = ProductRepo.find_by_id(product_id)
    if not product:
        flash('Product not found.', 'error')
        return redirect(url_for('admin_products'))
    
    review_count = ReviewRepo.delete_by_product(product_id)
    
    product_name = product.name
    ProductRepo.delete(product_id)
    flash(f'Product "{product_name}" and its {review_count} reviews deleted successfully!', 'success')
    
    return redirect(url_for('admin_products'))

@app.route('/admin/toggle_admin/<user_id>', methods=['POST'])
def toggle_admin(user_id):
    """Toggle admin privileges for a user"""
    current_user = get_current_user()
    if not current_user or not current_user.is_admin:
        flash('Access denied.', 'error')
        return redirect(url_for('index'))
    
    target_user = UserRepo.find_by_id(user_id)
    if not target_user:
        from flask import abort
        abort(404)
    
    if target_user.id == current_user.id:
        flash('You cannot remove admin privileges from yourself.', 'error')
        return redirect(url_for('admin_users'))
    
    UserRepo.update(user_id, {'is_admin': not target_user.is_admin})
    
    action = 'granted' if not target_user.is_admin else 'removed'
    flash(f'Admin privileges {action} for {target_user.username}.', 'success')
    return redirect(url_for('admin_users'))


# ============ SUPPORT TICKET ROUTES ============

@app.route('/support')
def support_center():
    """Support center - list user's tickets"""
    user = get_current_user()
    if not user:
        flash('Please login to access support center.', 'error')
        return redirect(url_for('login'))
    
    tickets = TicketRepo.find_by_user(user.id)
    return render_template('support/tickets.html', tickets=tickets)


@app.route('/support/new', methods=['GET', 'POST'])
def create_ticket():
    """Create a new support ticket"""
    user = get_current_user()
    if not user:
        flash('Please login to create a support ticket.', 'error')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        ticket_type = request.form.get('ticket_type')
        subject = request.form.get('subject', '').strip()
        description = request.form.get('description', '').strip()
        order_id = request.form.get('order_id') or None
        priority = request.form.get('priority', 'normal')
        
        if not ticket_type or not subject or not description:
            flash('Please fill in all required fields.', 'error')
            orders = OrderRepo.find_by_user(user.id)
            return render_template('support/create_ticket.html', orders=orders)
        
        ticket = TicketRepo.create({
            'user_id': user.id,
            'order_id': order_id,
            'ticket_type': ticket_type,
            'subject': subject,
            'description': description,
            'priority': priority
        })
        
        flash('Your support ticket has been created. We will respond shortly.', 'success')
        return redirect(url_for('view_ticket', ticket_id=ticket.id))
    
    orders = OrderRepo.find_by_user(user.id)
    return render_template('support/create_ticket.html', orders=orders)


@app.route('/support/ticket/<ticket_id>', methods=['GET', 'POST'])
def view_ticket(ticket_id):
    """View and respond to a support ticket"""
    user = get_current_user()
    if not user:
        flash('Please login to view tickets.', 'error')
        return redirect(url_for('login'))
    
    ticket = TicketRepo.find_by_id(ticket_id)
    if not ticket:
        flash('Ticket not found.', 'error')
        return redirect(url_for('support_center'))
    
    if str(ticket.user_id) != str(user.id) and not user.is_admin:
        flash('Access denied.', 'error')
        return redirect(url_for('support_center'))
    
    if request.method == 'POST':
        message = request.form.get('message', '').strip()
        if message:
            TicketMessageRepo.create({
                'ticket_id': ticket_id,
                'author_id': user.id,
                'message': message,
                'is_admin_reply': False
            })
            flash('Your message has been sent.', 'success')
            return redirect(url_for('view_ticket', ticket_id=ticket_id))
    
    messages = TicketMessageRepo.find_by_ticket(ticket_id)
    return render_template('support/view_ticket.html', ticket=ticket, messages=messages)


@app.route('/support/order/<order_id>')
def create_order_ticket(order_id):
    """Create a ticket for a specific order"""
    user = get_current_user()
    if not user:
        flash('Please login to create a support ticket.', 'error')
        return redirect(url_for('login'))
    
    order = OrderRepo.find_by_id(order_id)
    if not order or str(order.user_id) != str(user.id):
        flash('Order not found.', 'error')
        return redirect(url_for('user_orders'))
    
    orders = OrderRepo.find_by_user(user.id)
    return render_template('support/create_ticket.html', orders=orders, selected_order=order)


# ============ ADMIN TICKET ROUTES ============

@app.route('/admin/tickets')
def admin_tickets():
    """Admin view of all support tickets"""
    user = get_current_user()
    if not user or not user.is_admin:
        flash('Access denied.', 'error')
        return redirect(url_for('index'))
    
    status_filter = request.args.get('status', '')
    type_filter = request.args.get('type', '')
    
    tickets = TicketRepo.find_all(
        status=status_filter if status_filter else None,
        ticket_type=type_filter if type_filter else None
    )
    
    open_count = TicketRepo.count_by_status('open')
    in_progress_count = TicketRepo.count_by_status('in_progress')
    
    return render_template('admin/tickets.html', 
                          tickets=tickets, 
                          open_count=open_count,
                          in_progress_count=in_progress_count,
                          current_status=status_filter,
                          current_type=type_filter)


@app.route('/apply_coupon', methods=['POST'])
def apply_coupon():
    """Apply a coupon code to the session"""
    code = request.form.get('coupon_code', '').strip().upper()
    if not code:
        flash('Please enter a coupon code.', 'error')
        return redirect(url_for('checkout'))
    if not CouponRepo:
        flash('Coupons are not available.', 'error')
        return redirect(url_for('checkout'))

    coupon = CouponRepo.find_by_code(code)
    if not coupon:
        flash(f'Coupon "{code}" not found.', 'error')
        return redirect(url_for('checkout'))

    cart_total = get_cart_total()
    valid, msg = coupon.is_valid(cart_total)
    if not valid:
        flash(msg, 'error')
        return redirect(url_for('checkout'))

    discount = coupon.calculate_discount(cart_total)
    session['applied_coupon_code'] = coupon.code
    session['applied_coupon_discount'] = discount

    if coupon.discount_type == 'percentage':
        flash(f'Coupon "{code}" applied! You save {coupon.discount_value:.0f}% (₹{discount:.2f}) on your order.', 'success')
    else:
        flash(f'Coupon "{code}" applied! You save ₹{discount:.2f} on your order.', 'success')
    return redirect(url_for('checkout'))


@app.route('/remove_coupon', methods=['POST'])
def remove_coupon():
    """Remove applied coupon from session"""
    session.pop('applied_coupon_code', None)
    session.pop('applied_coupon_discount', None)
    flash('Coupon removed.', 'info')
    return redirect(url_for('checkout'))


@app.route('/admin/announcements')
def admin_announcements():
    user = get_current_user()
    if not user or not user.is_admin:
        flash('Access denied.', 'error')
        return redirect(url_for('index'))
    if not AnnouncementRepo:
        flash('Announcements require MongoDB.', 'error')
        return redirect(url_for('admin_dashboard'))
    announcements = AnnouncementRepo.find_all()
    return render_template('admin/announcements.html', announcements=announcements)


@app.route('/admin/announcements/add', methods=['POST'])
def admin_add_announcement():
    user = get_current_user()
    if not user or not user.is_admin:
        flash('Access denied.', 'error')
        return redirect(url_for('index'))

    from datetime import datetime as dt
    starts_at = None
    ends_at = None
    try:
        if request.form.get('starts_at'):
            starts_at = dt.strptime(request.form['starts_at'], '%Y-%m-%d')
        if request.form.get('ends_at'):
            ends_at = dt.strptime(request.form['ends_at'], '%Y-%m-%d')
    except:
        pass

    AnnouncementRepo.create({
        'text': request.form.get('text', '').strip(),
        'link_url': request.form.get('link_url', '').strip(),
        'link_text': request.form.get('link_text', '').strip(),
        'bg_color': request.form.get('bg_color', '#8B4513'),
        'text_color': request.form.get('text_color', '#ffffff'),
        'icon': request.form.get('icon', 'fas fa-bullhorn'),
        'is_active': True,
        'is_dismissible': bool(request.form.get('is_dismissible')),
        'priority': int(request.form.get('priority', 1)),
        'starts_at': starts_at,
        'ends_at': ends_at
    })
    flash('Announcement created!', 'success')
    return redirect(url_for('admin_announcements'))


@app.route('/admin/announcements/toggle/<ann_id>', methods=['POST'])
def admin_toggle_announcement(ann_id):
    user = get_current_user()
    if not user or not user.is_admin:
        flash('Access denied.', 'error')
        return redirect(url_for('index'))
    ann = AnnouncementRepo.find_by_id(ann_id)
    if ann:
        AnnouncementRepo.update(ann_id, {'is_active': not ann.is_active})
        flash(f'Announcement {"activated" if not ann.is_active else "paused"}.', 'success')
    return redirect(url_for('admin_announcements'))


@app.route('/admin/announcements/delete/<ann_id>', methods=['POST'])
def admin_delete_announcement(ann_id):
    user = get_current_user()
    if not user or not user.is_admin:
        flash('Access denied.', 'error')
        return redirect(url_for('index'))
    AnnouncementRepo.delete(ann_id)
    flash('Announcement deleted.', 'success')
    return redirect(url_for('admin_announcements'))


@app.route('/admin/coupons')
def admin_coupons():
    user = get_current_user()
    if not user or not user.is_admin:
        flash('Access denied.', 'error')
        return redirect(url_for('index'))
    if not CouponRepo:
        flash('Coupons require MongoDB.', 'error')
        return redirect(url_for('admin_dashboard'))
    coupons = CouponRepo.find_all()
    return render_template('admin/coupons.html', coupons=coupons, now=datetime.utcnow())


@app.route('/admin/coupons/add', methods=['POST'])
def admin_add_coupon():
    user = get_current_user()
    if not user or not user.is_admin:
        flash('Access denied.', 'error')
        return redirect(url_for('index'))
    code = request.form.get('code', '').strip().upper()
    if not code:
        flash('Coupon code is required.', 'error')
        return redirect(url_for('admin_coupons'))
    if CouponRepo.find_by_code(code):
        flash(f'Coupon "{code}" already exists.', 'error')
        return redirect(url_for('admin_coupons'))
    CouponRepo.create({
        'code': code,
        'description': request.form.get('description', '').strip(),
        'discount_type': request.form.get('discount_type', 'percentage'),
        'discount_value': request.form.get('discount_value', 0),
        'min_order_amount': request.form.get('min_order_amount', 0),
        'max_discount': request.form.get('max_discount', 0),
        'max_uses': request.form.get('max_uses', 0),
        'expires_at': request.form.get('expires_at', '')
    })
    flash(f'Coupon "{code}" created!', 'success')
    return redirect(url_for('admin_coupons'))


@app.route('/admin/coupons/toggle/<coupon_id>', methods=['POST'])
def admin_toggle_coupon(coupon_id):
    user = get_current_user()
    if not user or not user.is_admin:
        flash('Access denied.', 'error')
        return redirect(url_for('index'))
    coupon = CouponRepo.find_by_id(coupon_id)
    if coupon:
        CouponRepo.update(coupon_id, {'is_active': not coupon.is_active})
        flash(f'Coupon "{coupon.code}" {"activated" if not coupon.is_active else "deactivated"}.', 'success')
    return redirect(url_for('admin_coupons'))


@app.route('/admin/coupons/delete/<coupon_id>', methods=['POST'])
def admin_delete_coupon(coupon_id):
    user = get_current_user()
    if not user or not user.is_admin:
        flash('Access denied.', 'error')
        return redirect(url_for('index'))
    coupon = CouponRepo.find_by_id(coupon_id)
    if coupon:
        CouponRepo.delete(coupon_id)
        flash(f'Coupon "{coupon.code}" deleted.', 'success')
    return redirect(url_for('admin_coupons'))


@app.route('/admin/order/<order_id>')
def admin_order_detail(order_id):
    """Admin detailed order view page"""
    user = get_current_user()
    if not user or not user.is_admin:
        flash('Access denied.', 'error')
        return redirect(url_for('index'))

    order = OrderRepo.find_by_id(order_id)
    if not order:
        flash('Order not found.', 'error')
        return redirect(url_for('admin_orders'))

    order_items = []
    for item in order.items:
        if isinstance(item, dict):
            product_id = item.get('product_id')
            quantity = item.get('quantity', 1)
            price = item.get('price', 0)
            name = item.get('name', 'Product')
        else:
            product_id = getattr(item, 'product_id', None)
            quantity = getattr(item, 'quantity', 1)
            price = getattr(item, 'price', 0)
            name = getattr(item, 'name', 'Product')

        product = ProductRepo.find_by_id(product_id)
        order_items.append({
            'product': product,
            'name': name,
            'quantity': quantity,
            'price': price,
            'total': quantity * price
        })

    return render_template('admin/order_detail.html', order=order, order_items=order_items)


@app.route('/upload_payment_proof/<order_id>', methods=['POST'])
def upload_payment_proof(order_id):
    """Upload payment proof screenshot for QR/UPI orders"""
    import os, uuid
    from werkzeug.utils import secure_filename

    user = get_current_user()
    if not user:
        flash('Please login to continue.', 'error')
        return redirect(url_for('login'))

    order = OrderRepo.find_by_id(order_id)
    if not order or str(order.user_id) != str(user.id):
        flash('Order not found.', 'error')
        return redirect(url_for('index'))

    file = request.files.get('payment_proof')
    if not file or file.filename == '':
        flash('Please select a screenshot to upload.', 'error')
        return redirect(url_for('qr_payment'))

    allowed = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else ''
    if ext not in allowed:
        flash('Invalid file type. Please upload an image (PNG, JPG, GIF, WEBP).', 'error')
        return redirect(url_for('qr_payment'))

    upload_dir = os.path.join('static', 'uploads', 'payment_proofs')
    os.makedirs(upload_dir, exist_ok=True)
    filename = f"{order_id}_{uuid.uuid4().hex[:8]}.{ext}"
    file.save(os.path.join(upload_dir, filename))

    proof_url = f"uploads/payment_proofs/{filename}"
    OrderRepo.update(order_id, {
        'payment_proof_url': proof_url,
        'payment_proof_uploaded_at': datetime.utcnow(),
        'status': 'payment_proof_submitted'
    })

    session.pop('payment_order_id', None)
    session.pop('payment_amount', None)

    flash(f'Payment screenshot uploaded! Order #{order_id} is now pending admin verification.', 'success')
    return redirect(url_for('order_tracking', order_id=order_id))


@app.route('/admin/roles')
def admin_roles():
    """Admin role management page"""
    user = get_current_user()
    if not user or not user.is_admin:
        flash('Access denied.', 'error')
        return redirect(url_for('index'))
    if not RoleRepo:
        flash('Roles require MongoDB backend.', 'error')
        return redirect(url_for('admin_dashboard'))

    roles = RoleRepo.find_all()
    return render_template('admin/roles.html', roles=roles)


@app.route('/admin/roles/add', methods=['POST'])
def admin_add_role():
    """Add a custom role"""
    user = get_current_user()
    if not user or not user.is_admin:
        flash('Access denied.', 'error')
        return redirect(url_for('index'))

    name = request.form.get('name', '').strip().lower().replace(' ', '_')
    description = request.form.get('description', '').strip()
    permissions = [p.strip() for p in request.form.get('permissions', '').split(',') if p.strip()]

    if not name:
        flash('Role name is required.', 'error')
        return redirect(url_for('admin_roles'))

    if RoleRepo and RoleRepo.find_by_name(name):
        flash(f'Role "{name}" already exists.', 'error')
        return redirect(url_for('admin_roles'))

    RoleRepo.create({'name': name, 'description': description, 'permissions': permissions})
    flash(f'Role "{name}" created successfully!', 'success')
    return redirect(url_for('admin_roles'))


@app.route('/admin/roles/delete/<role_id>', methods=['POST'])
def admin_delete_role(role_id):
    """Delete a custom role"""
    user = get_current_user()
    if not user or not user.is_admin:
        flash('Access denied.', 'error')
        return redirect(url_for('index'))

    role = RoleRepo.find_by_id(role_id) if RoleRepo else None
    if not role:
        flash('Role not found.', 'error')
        return redirect(url_for('admin_roles'))
    if role.is_system:
        flash('System roles cannot be deleted.', 'error')
        return redirect(url_for('admin_roles'))

    RoleRepo.delete(role_id)
    flash(f'Role "{role.name}" deleted.', 'success')
    return redirect(url_for('admin_roles'))


@app.route('/admin/assign_role/<user_id>', methods=['POST'])
def admin_assign_role(user_id):
    """Assign a role to a user"""
    current = get_current_user()
    if not current or not current.is_admin:
        flash('Access denied.', 'error')
        return redirect(url_for('index'))

    role_name = request.form.get('role', '').strip()
    target = UserRepo.find_by_id(user_id)
    if not target:
        flash('User not found.', 'error')
        return redirect(url_for('admin_users'))

    is_admin = role_name == 'admin'
    UserRepo.update(user_id, {'role': role_name, 'is_admin': is_admin})
    flash(f'Role "{role_name}" assigned to {target.username}.', 'success')
    return redirect(url_for('admin_users'))


@app.route('/admin/ticket/<ticket_id>', methods=['GET', 'POST'])
def admin_view_ticket(ticket_id):
    """Admin view and manage a support ticket"""
    user = get_current_user()
    if not user or not user.is_admin:
        flash('Access denied.', 'error')
        return redirect(url_for('index'))
    
    ticket = TicketRepo.find_by_id(ticket_id)
    if not ticket:
        flash('Ticket not found.', 'error')
        return redirect(url_for('admin_tickets'))
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'reply':
            message = request.form.get('message', '').strip()
            if message:
                TicketMessageRepo.create({
                    'ticket_id': ticket_id,
                    'author_id': user.id,
                    'message': message,
                    'is_admin_reply': True
                })
                if ticket.status == 'open':
                    TicketRepo.update(ticket_id, {'status': 'in_progress'})
                flash('Reply sent successfully.', 'success')
        
        elif action == 'update_status':
            new_status = request.form.get('status')
            if new_status in ['open', 'in_progress', 'resolved', 'closed']:
                TicketRepo.update(ticket_id, {'status': new_status})
                flash(f'Ticket status updated to {new_status}.', 'success')
        
        elif action == 'update_priority':
            new_priority = request.form.get('priority')
            if new_priority in ['low', 'normal', 'high', 'urgent']:
                TicketRepo.update(ticket_id, {'priority': new_priority})
                flash(f'Ticket priority updated to {new_priority}.', 'success')
        
        return redirect(url_for('admin_view_ticket', ticket_id=ticket_id))
    
    messages = TicketMessageRepo.find_by_ticket(ticket_id)
    return render_template('admin/view_ticket.html', ticket=ticket, messages=messages)


@app.route('/admin/settings', methods=['GET', 'POST'])
def admin_settings():
    user = get_current_user()
    if not user or not user.is_admin:
        flash('Access denied.', 'error')
        return redirect(url_for('index'))

    if USE_MONGODB:
        from mongo_db import MongoSettingRepo
        from app import SETTING_DEFAULTS

        if request.method == 'POST':
            keys = [
                'site_name', 'site_tagline', 'contact_phone', 'contact_email',
                'hero_badge', 'hero_title', 'hero_highlight', 'hero_title_end', 'hero_subtitle',
                'free_delivery_min', 'about_year', 'about_lead', 'about_text',
                'cta_title', 'cta_subtitle', 'footer_text',
                'testimonial_1_name', 'testimonial_1_role', 'testimonial_1_img',
                'testimonial_2_name', 'testimonial_2_role', 'testimonial_2_img',
                'testimonial_3_name', 'testimonial_3_role', 'testimonial_3_img',
            ]
            data = {k: request.form.get(k, SETTING_DEFAULTS.get(k, '')) for k in keys}
            MongoSettingRepo.set_many(data)
            flash('Settings saved successfully!', 'success')
            return redirect(url_for('admin_settings'))

        saved = MongoSettingRepo.get_all()
        settings = dict(SETTING_DEFAULTS)
        settings.update(saved)
    else:
        from app import SETTING_DEFAULTS
        settings = dict(SETTING_DEFAULTS)

    return render_template('admin/settings.html', settings=settings)
