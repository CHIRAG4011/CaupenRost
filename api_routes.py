import logging
from flask import jsonify, request
from app import app, USE_MONGODB
from utils import (add_to_cart, remove_from_cart, update_cart_quantity,
                   get_cart, get_cart_total, get_cart_count)


def _product_to_dict(p):
    return {
        'id': str(p.id),
        'name': p.name,
        'price': float(p.price),
        'description': getattr(p, 'description', ''),
        'category': getattr(p, 'category', ''),
        'stock': getattr(p, 'stock', 0),
        'image_url': getattr(p, 'image_url', ''),
        'is_available': getattr(p, 'is_available', True),
    }


def _category_to_dict(c):
    return {
        'id': str(c.id),
        'name': c.name,
        'description': getattr(c, 'description', ''),
        'is_active': getattr(c, 'is_active', True),
    }


@app.route('/api/products', methods=['GET'])
def api_products():
    try:
        if USE_MONGODB:
            from mongo_db import MongoProductRepo as ProductRepo
        else:
            from db import ProductRepo
        products = ProductRepo.find_all()
        return jsonify({'success': True, 'products': [_product_to_dict(p) for p in products]})
    except Exception as e:
        logging.error(f"api_products error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/products/<product_id>', methods=['GET'])
def api_product_detail(product_id):
    try:
        if USE_MONGODB:
            from mongo_db import MongoProductRepo as ProductRepo
        else:
            from db import ProductRepo
        product = ProductRepo.find_by_id(product_id)
        if not product:
            return jsonify({'success': False, 'error': 'Product not found'}), 404
        return jsonify({'success': True, 'product': _product_to_dict(product)})
    except Exception as e:
        logging.error(f"api_product_detail error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/categories', methods=['GET'])
def api_categories():
    try:
        if USE_MONGODB:
            from mongo_db import MongoCategoryRepo as CategoryRepo
        else:
            from db import CategoryRepo
        categories = CategoryRepo.find_active()
        return jsonify({'success': True, 'categories': [_category_to_dict(c) for c in categories]})
    except Exception as e:
        logging.error(f"api_categories error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/cart', methods=['GET'])
def api_get_cart():
    try:
        cart = get_cart()
        items = []
        for pid, item in cart.items():
            items.append({
                'product_id': pid,
                'quantity': item['quantity'],
                'price': float(item['price']),
                'name': item.get('name', ''),
                'total': item['quantity'] * float(item['price']),
            })
        return jsonify({
            'success': True,
            'items': items,
            'count': get_cart_count(),
            'total': float(get_cart_total()),
        })
    except Exception as e:
        logging.error(f"api_get_cart error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/cart/add/<product_id>', methods=['POST'])
def api_add_to_cart(product_id):
    try:
        data = request.get_json(silent=True) or {}
        quantity = int(data.get('quantity', request.form.get('quantity', 1)))
        success = add_to_cart(product_id, quantity)
        return jsonify({
            'success': success,
            'message': 'Item added to cart!' if success else 'Unable to add item. Check stock.',
            'count': get_cart_count(),
            'total': float(get_cart_total()),
        })
    except Exception as e:
        logging.error(f"api_add_to_cart error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/cart/update', methods=['POST'])
def api_update_cart():
    try:
        data = request.get_json(silent=True) or {}
        product_id = data.get('product_id') or request.form.get('product_id')
        quantity = int(data.get('quantity', request.form.get('quantity', 1)))
        success = update_cart_quantity(product_id, quantity)
        return jsonify({
            'success': success,
            'message': 'Cart updated!' if success else 'Unable to update cart.',
            'count': get_cart_count(),
            'total': float(get_cart_total()),
        })
    except Exception as e:
        logging.error(f"api_update_cart error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/cart/remove/<product_id>', methods=['POST'])
def api_remove_from_cart(product_id):
    try:
        success = remove_from_cart(product_id)
        return jsonify({
            'success': success,
            'message': 'Item removed.' if success else 'Unable to remove item.',
            'count': get_cart_count(),
            'total': float(get_cart_total()),
        })
    except Exception as e:
        logging.error(f"api_remove_from_cart error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/health', methods=['GET'])
def api_health():
    return jsonify({'status': 'ok', 'service': 'CaupenRost API', 'db': 'mongodb' if USE_MONGODB else 'postgresql'})
