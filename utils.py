from flask import session
from flask_mail import Message
from app import mail, db
from models import User, Product, Order, Review, CartItem
import logging

def get_current_user():
    """Get current logged-in user"""
    user_id = session.get('user_id')
    if user_id:
        return User.query.get(user_id)
    return None

def get_cart():
    """Get current user's cart"""
    if 'cart' not in session:
        session['cart'] = {}
    return session['cart']

def add_to_cart(product_id, quantity=1):
    """Add item to cart"""
    cart = get_cart()
    product = Product.query.get(product_id)
    
    if not product:
        return False
    
    if product.stock < quantity:
        return False
    
    product_id_str = str(product_id)
    if product_id_str in cart:
        cart[product_id_str]['quantity'] += quantity
    else:
        cart[product_id_str] = {
            'quantity': quantity,
            'price': product.price,
            'name': product.name
        }
    
    session['cart'] = cart
    return True

def remove_from_cart(product_id):
    """Remove item from cart"""
    cart = get_cart()
    product_id_str = str(product_id)
    if product_id_str in cart:
        del cart[product_id_str]
        session['cart'] = cart
        return True
    return False

def update_cart_quantity(product_id, quantity):
    """Update item quantity in cart"""
    cart = get_cart()
    product_id_str = str(product_id)
    product = Product.query.get(product_id)
    
    if product_id_str in cart and product and product.stock >= quantity:
        if quantity <= 0:
            del cart[product_id_str]
        else:
            cart[product_id_str]['quantity'] = quantity
        session['cart'] = cart
        return True
    return False

def get_cart_total():
    """Calculate cart total"""
    cart = get_cart()
    total = 0
    for item in cart.values():
        total += item['quantity'] * item['price']
    return total

def get_cart_count():
    """Get total items in cart"""
    cart = get_cart()
    return sum(item['quantity'] for item in cart.values())

def clear_cart():
    """Clear the cart"""
    session['cart'] = {}
    session.modified = True

def send_order_confirmation_email(user_email, order):
    """Send order confirmation email"""
    try:
        msg = Message(
            subject=f'Order Confirmation - #{order.id}',
            recipients=[user_email],
            body=f'''
Dear Customer,

Thank you for your order at NIKITA RASOI & BAKES!

Order Details:
Order ID: #{order.id}
Total: ₹{order.total:.2f}
Status: {order.status.title()}

Your delicious baked goods will be prepared with care and delivered to:
{order.shipping_address}

You can track your order status in your account dashboard.

Thank you for choosing NIKITA RASOI & BAKES!

Best regards,
The NIKITA RASOI & BAKES Team
            '''
        )
        mail.send(msg)
        logging.info(f"Order confirmation email sent to {user_email}")
        return True
    except Exception as e:
        logging.error(f"Failed to send email: {str(e)}")
        return False

def calculate_order_stats():
    """Calculate order statistics for admin dashboard"""
    orders = Order.query.all()
    
    total_orders = len(orders)
    total_revenue = sum(order.total for order in orders)
    
    pending_orders = Order.query.filter_by(status='pending').count()
    completed_orders = Order.query.filter_by(status='delivered').count()
    
    return {
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'pending_orders': pending_orders,
        'completed_orders': completed_orders
    }

def search_products(query, category=None):
    """Search products by name and optionally filter by category"""
    products_query = Product.query
    
    if category and category != 'all':
        products_query = products_query.filter(Product.category.ilike(category))
    
    if query:
        search_term = f"%{query}%"
        products_query = products_query.filter(
            db.or_(
                Product.name.ilike(search_term),
                Product.description.ilike(search_term)
            )
        )
    
    return products_query.all()
