"""
CaupenRost — Standalone API Server
Runs on port 8080, serves pure JSON responses with CORS enabled.
Cart state is stored in MongoDB (keyed by cart_id cookie) so it works
independently of the main Flask session on port 5000.
"""
import os
import uuid
import logging

from flask import Flask, jsonify, request, make_response
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

logging.basicConfig(level=logging.INFO)

api_app = Flask(__name__)
api_app.secret_key = os.environ.get("SESSION_SECRET", "api-dev-secret")
api_app.wsgi_app = ProxyFix(api_app.wsgi_app, x_proto=1, x_host=1)

CORS(api_app, supports_credentials=True, origins="*")

USE_MONGODB = bool(os.environ.get('MONGO_URI')) or (
    os.environ.get('DATABASE_URL') and 'mongodb' in os.environ.get('DATABASE_URL', '')
)

_mongo_db = None


def get_db():
    global _mongo_db
    if _mongo_db is not None:
        return _mongo_db
    mongo_uri = (os.environ.get('MONGO_URI') or '').strip()
    if not mongo_uri:
        return None
    try:
        from pymongo import MongoClient
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        client.server_info()
        db_name = mongo_uri.split('/')[-1].split('?')[0].strip() or 'caupenrost'
        _mongo_db = client[db_name]
        logging.info(f"API server connected to MongoDB: {db_name}")
        return _mongo_db
    except Exception as e:
        logging.error(f"API server MongoDB connection failed: {e}")
        return None


def get_cart_id():
    return request.cookies.get('api_cart_id') or str(uuid.uuid4())


def get_cart_from_db(cart_id):
    db = get_db()
    if db is None:
        return {}
    doc = db.api_carts.find_one({'cart_id': cart_id})
    return doc.get('items', {}) if doc else {}


def save_cart_to_db(cart_id, cart):
    db = get_db()
    if db is None:
        return
    db.api_carts.update_one(
        {'cart_id': cart_id},
        {'$set': {'items': cart}},
        upsert=True
    )


def cart_count(cart):
    return sum(item['quantity'] for item in cart.values())


def cart_total(cart):
    return sum(item['quantity'] * item['price'] for item in cart.values())


def _product_to_dict(p):
    doc = dict(p) if isinstance(p, dict) else {}
    if not doc and hasattr(p, '__dict__'):
        doc = {k: v for k, v in p.__dict__.items() if not k.startswith('_')}
    doc['id'] = str(doc.get('_id') or doc.get('id', ''))
    doc.pop('_id', None)
    for k in ('price',):
        if k in doc:
            try:
                doc[k] = float(doc[k])
            except Exception:
                pass
    return doc


def _with_cart_cookie(response, cart_id):
    response.set_cookie('api_cart_id', cart_id, httponly=True, samesite='None', secure=True, max_age=60*60*24*30)
    return response


@api_app.route('/api/health', methods=['GET'])
def health():
    db = get_db()
    return jsonify({'status': 'ok', 'service': 'CaupenRost API Server', 'db': 'mongodb' if db is not None else 'unavailable'})


@api_app.route('/api/products', methods=['GET'])
def products():
    db = get_db()
    if db is None:
        return jsonify({'success': False, 'error': 'Database unavailable'}), 503
    try:
        query = request.args.get('q', '').strip()
        category = request.args.get('category', '').strip()
        filter_q = {}
        if query:
            filter_q['$or'] = [
                {'name': {'$regex': query, '$options': 'i'}},
                {'description': {'$regex': query, '$options': 'i'}},
            ]
        if category and category != 'all':
            filter_q['category'] = category
        items = list(db.products.find(filter_q))
        result = []
        for p in items:
            p['id'] = str(p.pop('_id'))
            p['price'] = float(p.get('price', 0))
            result.append(p)
        return jsonify({'success': True, 'products': result})
    except Exception as e:
        logging.error(f"products error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_app.route('/api/products/<product_id>', methods=['GET'])
def product_detail(product_id):
    db = get_db()
    if db is None:
        return jsonify({'success': False, 'error': 'Database unavailable'}), 503
    try:
        from bson import ObjectId
        p = db.products.find_one({'_id': ObjectId(product_id)})
        if not p:
            return jsonify({'success': False, 'error': 'Product not found'}), 404
        p['id'] = str(p.pop('_id'))
        p['price'] = float(p.get('price', 0))
        return jsonify({'success': True, 'product': p})
    except Exception as e:
        logging.error(f"product_detail error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_app.route('/api/categories', methods=['GET'])
def categories():
    db = get_db()
    if db is None:
        return jsonify({'success': False, 'error': 'Database unavailable'}), 503
    try:
        items = list(db.categories.find({'is_active': True}))
        result = []
        for c in items:
            c['id'] = str(c.pop('_id'))
            result.append(c)
        return jsonify({'success': True, 'categories': result})
    except Exception as e:
        logging.error(f"categories error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_app.route('/api/cart', methods=['GET'])
def get_cart():
    cart_id = get_cart_id()
    cart = get_cart_from_db(cart_id)
    items = [{'product_id': pid, **item, 'price': float(item['price']),
               'total': item['quantity'] * float(item['price'])}
             for pid, item in cart.items()]
    resp = make_response(jsonify({
        'success': True,
        'cart_id': cart_id,
        'items': items,
        'count': cart_count(cart),
        'total': float(cart_total(cart)),
    }))
    return _with_cart_cookie(resp, cart_id)


@api_app.route('/api/cart/add/<product_id>', methods=['POST'])
def add_to_cart(product_id):
    db = get_db()
    if db is None:
        return jsonify({'success': False, 'error': 'Database unavailable'}), 503
    try:
        from bson import ObjectId
        cart_id = get_cart_id()
        cart = get_cart_from_db(cart_id)
        data = request.get_json(silent=True) or {}
        quantity = int(data.get('quantity', 1))
        p = db.products.find_one({'_id': ObjectId(product_id)})
        if not p:
            return jsonify({'success': False, 'error': 'Product not found'}), 404
        stock = int(p.get('stock', 0))
        if stock < quantity:
            return jsonify({'success': False, 'error': 'Insufficient stock'}), 400
        pid_str = str(product_id)
        if pid_str in cart:
            cart[pid_str]['quantity'] += quantity
        else:
            cart[pid_str] = {'quantity': quantity, 'price': float(p['price']), 'name': p.get('name', '')}
        save_cart_to_db(cart_id, cart)
        resp = make_response(jsonify({
            'success': True,
            'message': 'Item added to cart!',
            'count': cart_count(cart),
            'total': float(cart_total(cart)),
        }))
        return _with_cart_cookie(resp, cart_id)
    except Exception as e:
        logging.error(f"add_to_cart error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_app.route('/api/cart/update', methods=['POST'])
def update_cart():
    try:
        cart_id = get_cart_id()
        cart = get_cart_from_db(cart_id)
        data = request.get_json(silent=True) or {}
        product_id = str(data.get('product_id', ''))
        quantity = int(data.get('quantity', 1))
        if product_id not in cart:
            return jsonify({'success': False, 'error': 'Item not in cart'}), 404
        if quantity <= 0:
            del cart[product_id]
        else:
            cart[product_id]['quantity'] = quantity
        save_cart_to_db(cart_id, cart)
        resp = make_response(jsonify({
            'success': True,
            'message': 'Cart updated!',
            'count': cart_count(cart),
            'total': float(cart_total(cart)),
        }))
        return _with_cart_cookie(resp, cart_id)
    except Exception as e:
        logging.error(f"update_cart error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_app.route('/api/cart/remove/<product_id>', methods=['POST'])
def remove_from_cart(product_id):
    try:
        cart_id = get_cart_id()
        cart = get_cart_from_db(cart_id)
        pid_str = str(product_id)
        if pid_str in cart:
            del cart[pid_str]
            save_cart_to_db(cart_id, cart)
            success = True
        else:
            success = False
        resp = make_response(jsonify({
            'success': success,
            'message': 'Item removed.' if success else 'Item not found in cart.',
            'count': cart_count(cart),
            'total': float(cart_total(cart)),
        }))
        return _with_cart_cookie(resp, cart_id)
    except Exception as e:
        logging.error(f"remove_from_cart error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


if __name__ == '__main__':
    api_app.run(host='0.0.0.0', port=8080, debug=True)
