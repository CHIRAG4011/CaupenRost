import os
import logging
import resend
from flask import session
from app import USE_MONGODB

if USE_MONGODB:
    from mongo_db import MongoUserRepo as UserRepo, MongoProductRepo as ProductRepo, MongoOrderRepo as OrderRepo
else:
    from db import UserRepo, ProductRepo, OrderRepo


def get_current_user():
    """Get current logged-in user"""
    user_id = session.get('user_id')
    if user_id:
        return UserRepo.find_by_id(user_id)
    return None


def get_cart():
    """Get current user's cart"""
    if 'cart' not in session:
        session['cart'] = {}
    return session['cart']


def add_to_cart(product_id, quantity=1):
    """Add item to cart"""
    cart = get_cart()
    product = ProductRepo.find_by_id(product_id)

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
    product = ProductRepo.find_by_id(product_id)

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
    """Send order confirmation email via Resend"""
    api_key = os.environ.get('RESEND_API_KEY', '').strip()
    if not api_key:
        logging.warning("RESEND_API_KEY not set — skipping order confirmation email")
        return False

    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
            <h1 style="color: white; margin: 0;">CaupenRost</h1>
        </div>
        <div style="background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px;">
            <h2 style="color: #333;">Order Confirmed!</h2>
            <p style="color: #666; font-size: 16px;">Thank you for your order at CaupenRost!</p>
            <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
                <tr><td style="padding: 8px; color: #666;">Order ID:</td><td style="padding: 8px; font-weight: bold;">#{order.id}</td></tr>
                <tr><td style="padding: 8px; color: #666;">Total:</td><td style="padding: 8px; font-weight: bold;">&#8377;{order.total:.2f}</td></tr>
                <tr><td style="padding: 8px; color: #666;">Status:</td><td style="padding: 8px; font-weight: bold;">{order.status.title()}</td></tr>
                <tr><td style="padding: 8px; color: #666;">Delivery to:</td><td style="padding: 8px;">{order.shipping_address}</td></tr>
            </table>
            <p style="color: #666; font-size: 14px;">You can track your order status in your account dashboard.</p>
            <p style="color: #999; font-size: 12px;">Thank you for choosing CaupenRost!</p>
        </div>
    </div>
    """

    try:
        resend.api_key = api_key
        resend.Emails.send({
            "from": "CaupenRost <onboarding@resend.dev>",
            "to": [user_email],
            "subject": f"Order Confirmation - #{order.id}",
            "html": html,
        })
        logging.info(f"Order confirmation email sent to {user_email}")
        return True
    except Exception as e:
        logging.error(f"Failed to send order confirmation email: {e}")
        return False


def calculate_order_stats():
    """Calculate order statistics for admin dashboard"""
    total_orders = OrderRepo.count()
    total_revenue = OrderRepo.sum_total()
    pending_orders = OrderRepo.count_by_status('pending')
    completed_orders = OrderRepo.count_by_status('delivered')

    return {
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'pending_orders': pending_orders,
        'completed_orders': completed_orders
    }


def search_products(query, category=None):
    """Search products by name and optionally filter by category"""
    return ProductRepo.search(query, category)
