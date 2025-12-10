from flask import render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from app import app, db
from models import User, Product, Order, Review, Address, OrderItem, VisitorLog, Category
from data_store import add_visitor_log, get_weekly_visitors
from utils import (get_current_user, add_to_cart, remove_from_cart, update_cart_quantity, 
                  get_cart_total, get_cart_count, clear_cart, send_order_confirmation_email,
                  calculate_order_stats, search_products, get_cart)
from email_service import send_and_store_otp, verify_otp
import logging
from datetime import datetime
import json

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
    return {
        'current_user': get_current_user(),
        'cart_count': get_cart_count(),
        'cart_total': get_cart_total()
    }

@app.route('/')
def index():
    """Home page"""
    featured_products = Product.query.limit(6).all()
    return render_template('index.html', featured_products=featured_products)

@app.route('/products')
def products():
    """Products page with search and filter"""
    query = request.args.get('q', '')
    category = request.args.get('category', 'all')
    
    if query or category != 'all':
        product_list = search_products(query, category)
    else:
        product_list = Product.query.all()
    
    categories = [cat.name for cat in Category.query.filter_by(is_active=True).all()]
    
    return render_template('products.html', 
                         products=product_list, 
                         categories=categories,
                         current_query=query,
                         current_category=category)

@app.route('/categories')
def categories():
    """Categories page showing all available categories"""
    active_categories = Category.query.filter_by(is_active=True).all()
    return render_template('categories.html', categories=active_categories)

@app.route('/category/<category_name>')
def category_products(category_name):
    """Show products for a specific category"""
    category = Category.query.filter_by(name=category_name, is_active=True).first()
    
    if not category:
        flash('Category not found.', 'error')
        return redirect(url_for('products'))
    
    category_products_list = Product.query.filter_by(category=category_name).all()
    
    return render_template('category_products.html', 
                         category=category, 
                         products=category_products_list)

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    """Product detail page"""
    product = Product.query.get(product_id)
    if not product:
        from flask import abort
        abort(404)
    
    product_reviews = Review.query.filter_by(product_id=product_id).all()
    
    return render_template('product_detail.html', product=product, reviews=product_reviews)

@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
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
        product_id = int(product_id_str)
        product = Product.query.get(product_id)
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
    product_id = int(request.form.get('product_id', '0'))
    quantity = int(request.form.get('quantity', '1'))
    
    if update_cart_quantity(product_id, quantity):
        flash('Cart updated!', 'success')
    else:
        flash('Unable to update cart.', 'error')
    
    return redirect(url_for('cart'))

@app.route('/remove_from_cart/<int:product_id>')
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
    
    user_addresses = Address.query.filter_by(user_id=user.id).all()
    
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
        address = Address.query.get(int(address_id))
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
    delivery_fee = 50.00
    tax_amount = (cart_total + delivery_fee) * 0.18
    final_amount = cart_total + delivery_fee + tax_amount
    
    if payment_method == 'cash_on_delivery':
        final_amount += 20.00
    
    for product_id_str, item_data in cart_data.items():
        product_id = int(product_id_str)
        product = Product.query.get(product_id)
        
        if not product or product.stock < item_data['quantity']:
            flash(f'Insufficient stock for {product.name if product else "unknown item"}.', 'error')
            return redirect(url_for('cart'))
    
    session['pending_order'] = {
        'shipping_address': shipping_address,
        'payment_method': payment_method,
        'final_amount': final_amount
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
            
            order = Order(
                user_id=user.id,
                total=pending['final_amount'],
                shipping_address=pending['shipping_address'],
                status=status,
                payment_method=pending['payment_method']
            )
            db.session.add(order)
            db.session.flush()
            
            for product_id_str, item_data in cart_data.items():
                product_id = int(product_id_str)
                product = Product.query.get(product_id)
                
                if not product or product.stock < item_data['quantity']:
                    db.session.rollback()
                    flash(f'Insufficient stock for {product.name if product else "unknown item"}.', 'error')
                    session.pop('pending_order', None)
                    return redirect(url_for('cart'))
                
                order_item = OrderItem(
                    order_id=order.id,
                    product_id=product_id,
                    quantity=item_data['quantity'],
                    price=item_data['price']
                )
                db.session.add(order_item)
                
                product.stock -= item_data['quantity']
            
            db.session.commit()
            
            try:
                send_order_confirmation_email(user.email, order)
            except Exception as e:
                logging.warning(f"Failed to send confirmation email: {e}")
            
            clear_cart()
            session.pop('pending_order', None)
            
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
    
    order = Order.query.get(order_id)
    if not order:
        flash('Order not found.', 'error')
        return redirect(url_for('index'))
    
    return render_template('qr_payment.html', 
                         order_id=order_id, 
                         amount=amount,
                         order=order)

@app.route('/confirm_payment/<int:order_id>', methods=['POST'])
def confirm_payment(order_id):
    """Confirm QR code payment"""
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Please login to proceed'}), 401
    
    order = Order.query.get(order_id)
    if not order or order.user_id != user.id:
        return jsonify({'error': 'Order not found'}), 404
    
    order.status = 'confirmed'
    order.updated_at = datetime.now()
    db.session.commit()
    
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
        
        # Password requirements validation
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
        
        existing_user = User.query.filter(
            (User.username == username) | (User.email == email)
        ).first()
        
        if existing_user:
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
            user = User(
                username=pending['username'],
                email=pending['email'],
                password_hash=generate_password_hash(pending['password'] or '')
            )
            
            db.session.add(user)
            db.session.commit()
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
        
        user = User.query.filter(
            (User.username == username) | (User.email == username)
        ).first()
        
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
    
    user_addresses = Address.query.filter_by(user_id=user.id).all()
    
    return render_template('user/profile.html', addresses=user_addresses)

@app.route('/add_address', methods=['POST'])
def add_address():
    """Add a new address"""
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))
    
    address = Address(
        user_id=user.id,
        name=request.form.get('name'),
        street=request.form.get('street'),
        city=request.form.get('city'),
        state=request.form.get('state'),
        zip_code=request.form.get('zip_code')
    )
    
    db.session.add(address)
    db.session.commit()
    flash('Address added successfully!', 'success')
    return redirect(url_for('profile'))

@app.route('/orders')
def user_orders():
    """User orders page"""
    user = get_current_user()
    if not user:
        flash('Please login to view your orders.', 'error')
        return redirect(url_for('login'))
    
    user_orders_list = Order.query.filter_by(user_id=user.id).order_by(Order.created_at.desc()).all()
    
    return render_template('user/orders.html', orders=user_orders_list)

@app.route('/order/<int:order_id>')
def order_tracking(order_id):
    """Order tracking page"""
    order = Order.query.get(order_id)
    if not order:
        flash('Order not found.', 'error')
        return redirect(url_for('user_orders'))
    
    user = get_current_user()
    if not user or (order.user_id != user.id and not user.is_admin):
        flash('Unauthorized access.', 'error')
        return redirect(url_for('index'))
    
    order_items = []
    for item in order.items.all():
        product = Product.query.get(item.product_id)
        if product:
            order_items.append({
                'product': product,
                'quantity': item.quantity,
                'price': item.price,
                'total': item.quantity * item.price
            })
    
    return render_template('user/order_detail.html', order=order, order_items=order_items)

@app.route('/add_review/<int:product_id>', methods=['POST'])
def add_review(product_id):
    """Add a product review"""
    user = get_current_user()
    if not user:
        flash('Please login to add a review.', 'error')
        return redirect(url_for('login'))
    
    rating = int(request.form.get('rating', '1'))
    comment = request.form.get('comment')
    
    review = Review(
        product_id=product_id,
        user_id=user.id,
        rating=rating,
        comment=comment
    )
    
    db.session.add(review)
    db.session.commit()
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
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(10).all()
    
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
    
    products = Product.query.all()
    categories = Category.query.all()
    return render_template('admin/products.html', products=products, categories=categories)

@app.route('/admin/add_product', methods=['POST'])
def admin_add_product():
    """Add a new product"""
    user = get_current_user()
    if not user or not user.is_admin:
        return redirect(url_for('index'))
    
    category_name = request.form.get('category')
    cat = Category.query.filter_by(name=category_name).first()
    
    product = Product(
        name=request.form.get('name'),
        description=request.form.get('description'),
        price=float(request.form.get('price', '0')),
        category=category_name,
        category_id=cat.id if cat else None,
        image_url=request.form.get('image_url'),
        stock=int(request.form.get('stock', '0'))
    )
    
    db.session.add(product)
    db.session.commit()
    flash('Product added successfully!', 'success')
    return redirect(url_for('admin_products'))

@app.route('/admin/update_stock/<int:product_id>', methods=['POST'])
def admin_update_stock(product_id):
    """Update product stock"""
    user = get_current_user()
    if not user or not user.is_admin:
        return redirect(url_for('index'))
    
    product = Product.query.get(product_id)
    if product:
        product.stock = int(request.form.get('stock', '0'))
        db.session.commit()
        flash('Stock updated successfully!', 'success')
    
    return redirect(url_for('admin_products'))

@app.route('/admin/edit_product', methods=['POST'])
def admin_edit_product():
    """Edit an existing product"""
    user = get_current_user()
    if not user or not user.is_admin:
        return redirect(url_for('index'))
    
    product_id_str = request.form.get('product_id')
    if not product_id_str:
        flash('Product ID is required.', 'error')
        return redirect(url_for('admin_products'))
    product_id = int(product_id_str)
    product = Product.query.get(product_id)
    
    if product:
        category_name = request.form.get('category')
        cat = Category.query.filter_by(name=category_name).first()
        
        product.name = request.form.get('name')
        product.description = request.form.get('description')
        product.price = float(request.form.get('price', '0'))
        product.category = category_name
        product.category_id = cat.id if cat else None
        product.image_url = request.form.get('image_url')
        product.stock = int(request.form.get('stock', '0'))
        db.session.commit()
        flash('Product updated successfully!', 'success')
    
    return redirect(url_for('admin_products'))

@app.route('/admin/orders')
def admin_orders():
    """Admin orders management"""
    user = get_current_user()
    if not user or not user.is_admin:
        flash('Access denied.', 'error')
        return redirect(url_for('index'))
    
    orders = Order.query.order_by(Order.created_at.desc()).all()
    
    return render_template('admin/orders.html', orders=orders)

@app.route('/admin/update_order_status/<int:order_id>', methods=['POST'])
def admin_update_order_status(order_id):
    """Update order status"""
    user = get_current_user()
    if not user or not user.is_admin:
        return redirect(url_for('index'))
    
    order = Order.query.get(order_id)
    if order:
        new_status = request.form.get('status')
        order.update_status(new_status)
        db.session.commit()
        flash('Order status updated successfully!', 'success')
    
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
    
    return render_template('admin/analytics.html', 
                         weekly_visitors=weekly_visitors,
                         stats=stats)

@app.route('/admin/users')
def admin_users():
    """Admin user management"""
    user = get_current_user()
    if not user or not user.is_admin:
        flash('Access denied.', 'error')
        return redirect(url_for('index'))
    
    users = User.query.all()
    return render_template('admin/users.html', users=users)

@app.route('/admin/categories')
def admin_categories():
    """Admin category management"""
    user = get_current_user()
    if not user or not user.is_admin:
        flash('Access denied.', 'error')
        return redirect(url_for('index'))
    
    categories = Category.query.all()
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
        
        existing_category = Category.query.filter(
            db.func.lower(Category.name) == name.lower()
        ).first()
        
        if existing_category:
            flash('Category with this name already exists.', 'error')
            return render_template('admin/add_category.html')
        
        new_category = Category(
            name=name,
            description=description,
            image_url=image_url
        )
        
        db.session.add(new_category)
        db.session.commit()
        flash(f'Category "{name}" added successfully!', 'success')
        return redirect(url_for('admin_categories'))
    
    return render_template('admin/add_category.html')

@app.route('/admin/edit_category/<int:category_id>', methods=['GET', 'POST'])
def admin_edit_category(category_id):
    """Edit existing category"""
    user = get_current_user()
    if not user or not user.is_admin:
        flash('Access denied.', 'error')
        return redirect(url_for('index'))
    
    category = Category.query.get(category_id)
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
        
        existing_category = Category.query.filter(
            db.func.lower(Category.name) == name.lower(),
            Category.id != category_id
        ).first()
        
        if existing_category:
            flash('Category with this name already exists.', 'error')
            return render_template('admin/edit_category.html', category=category)
        
        category.name = name
        category.description = description
        category.image_url = image_url
        category.is_active = is_active
        db.session.commit()
        
        flash(f'Category "{name}" updated successfully!', 'success')
        return redirect(url_for('admin_categories'))
    
    return render_template('admin/edit_category.html', category=category)

@app.route('/admin/toggle_category_status/<int:category_id>', methods=['POST'])
def admin_toggle_category_status(category_id):
    """Toggle category active status"""
    user = get_current_user()
    if not user or not user.is_admin:
        flash('Access denied.', 'error')
        return redirect(url_for('index'))
    
    category = Category.query.get(category_id)
    if not category:
        flash('Category not found.', 'error')
        return redirect(url_for('admin_categories'))
    
    category.is_active = not category.is_active
    db.session.commit()
    status = "activated" if category.is_active else "deactivated"
    flash(f'Category "{category.name}" {status} successfully!', 'success')
    
    return redirect(url_for('admin_categories'))

@app.route('/admin/delete_category/<int:category_id>', methods=['POST', 'GET'])
def admin_delete_category(category_id):
    """Delete a category"""
    user = get_current_user()
    if not user or not user.is_admin:
        flash('Access denied.', 'error')
        return redirect(url_for('index'))
    
    category = Category.query.get(category_id)
    if not category:
        flash('Category not found.', 'error')
        return redirect(url_for('admin_categories'))
    
    products_in_category = Product.query.filter_by(category=category.name).all()
    if products_in_category:
        flash(f'Cannot delete category "{category.name}" because it contains {len(products_in_category)} products. Please move or delete these products first.', 'error')
        return redirect(url_for('admin_categories'))
    
    category_name = category.name
    db.session.delete(category)
    db.session.commit()
    flash(f'Category "{category_name}" deleted successfully!', 'success')
    
    return redirect(url_for('admin_categories'))

@app.route('/admin/delete_product/<int:product_id>', methods=['POST'])
def admin_delete_product(product_id):
    """Delete a product"""
    user = get_current_user()
    if not user or not user.is_admin:
        flash('Access denied.', 'error')
        return redirect(url_for('index'))
    
    product = Product.query.get(product_id)
    if not product:
        flash('Product not found.', 'error')
        return redirect(url_for('admin_products'))
    
    reviews_to_delete = Review.query.filter_by(product_id=product_id).all()
    review_count = len(reviews_to_delete)
    for review in reviews_to_delete:
        db.session.delete(review)
    
    product_name = product.name
    db.session.delete(product)
    db.session.commit()
    flash(f'Product "{product_name}" and its {review_count} reviews deleted successfully!', 'success')
    
    return redirect(url_for('admin_products'))

@app.route('/admin/toggle_admin/<int:user_id>', methods=['POST'])
def toggle_admin(user_id):
    """Toggle admin privileges for a user"""
    current_user = get_current_user()
    if not current_user or not current_user.is_admin:
        flash('Access denied.', 'error')
        return redirect(url_for('index'))
    
    target_user = User.query.get(user_id)
    if not target_user:
        from flask import abort
        abort(404)
    
    if target_user.id == current_user.id:
        flash('You cannot remove admin privileges from yourself.', 'error')
        return redirect(url_for('admin_users'))
    
    target_user.is_admin = not target_user.is_admin
    db.session.commit()
    
    action = 'granted' if target_user.is_admin else 'removed'
    flash(f'Admin privileges {action} for {target_user.username}.', 'success')
    return redirect(url_for('admin_users'))
