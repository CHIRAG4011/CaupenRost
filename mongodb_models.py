from datetime import datetime
from werkzeug.security import check_password_hash, generate_password_hash
from bson import ObjectId


class ReviewsList(list):
    """Wrapper around list to provide .all() method for SQLAlchemy compatibility"""
    def all(self):
        return list(self)


class MongoUser:
    collection_name = 'users'
    
    def __init__(self, data):
        self._id = data.get('_id')
        self.id = str(data.get('_id')) if data.get('_id') else None
        self.username = data.get('username')
        self.email = data.get('email')
        self.password_hash = data.get('password_hash')
        self.is_admin = data.get('is_admin', False)
        self.created_at = data.get('created_at', datetime.utcnow())
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_authenticated(self):
        return True
    
    def is_active(self):
        return True
    
    def is_anonymous(self):
        return False
    
    def get_id(self):
        return str(self._id)
    
    def to_dict(self):
        return {
            'username': self.username,
            'email': self.email,
            'password_hash': self.password_hash,
            'is_admin': self.is_admin,
            'created_at': self.created_at
        }
    
    @classmethod
    def from_doc(cls, doc):
        if doc is None:
            return None
        return cls(doc)


class MongoCategory:
    collection_name = 'categories'
    
    def __init__(self, data):
        self._id = data.get('_id')
        self.id = str(data.get('_id')) if data.get('_id') else None
        self.name = data.get('name')
        self.description = data.get('description', '')
        self.image_url = data.get('image_url', '')
        self.is_active = data.get('is_active', True)
        self.created_at = data.get('created_at', datetime.utcnow())
    
    def get_product_count(self):
        """Get count of products in this category"""
        from mongo_db import MongoProductRepo
        products = MongoProductRepo.find_by_category(self.name)
        return len(products) if products else 0
    
    def to_dict(self):
        return {
            'name': self.name,
            'description': self.description,
            'image_url': self.image_url,
            'is_active': self.is_active,
            'created_at': self.created_at
        }
    
    @classmethod
    def from_doc(cls, doc):
        if doc is None:
            return None
        return cls(doc)


class MongoProduct:
    collection_name = 'products'
    
    def __init__(self, data):
        self._id = data.get('_id')
        self.id = str(data.get('_id')) if data.get('_id') else None
        self.name = data.get('name')
        self.description = data.get('description')
        self.price = data.get('price', 0)
        self.category = data.get('category')
        self.category_id = data.get('category_id')
        self.image_url = data.get('image_url')
        self.stock = data.get('stock', 0)
        self.created_at = data.get('created_at', datetime.utcnow())
        self.reviews = ReviewsList()
    
    def get_average_rating(self):
        if not self.reviews:
            return 0
        total = sum(r.rating for r in self.reviews)
        return total / len(self.reviews) if self.reviews else 0
    
    def to_dict(self):
        return {
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'category': self.category,
            'category_id': self.category_id,
            'image_url': self.image_url,
            'stock': self.stock,
            'created_at': self.created_at
        }
    
    @classmethod
    def from_doc(cls, doc):
        if doc is None:
            return None
        return cls(doc)


class OrderItem:
    """Wrapper to make order item dicts accessible as objects with attributes"""
    def __init__(self, data):
        self.product_id = data.get('product_id')
        self.name = data.get('name', 'Product')
        self.quantity = data.get('quantity', 1)
        self.price = data.get('price', 0)
    
    def get(self, key, default=None):
        return getattr(self, key, default)


class MongoOrder:
    collection_name = 'orders'
    
    def __init__(self, data):
        self._id = data.get('_id')
        self.id = str(data.get('_id')) if data.get('_id') else None
        self.user_id = data.get('user_id')
        self.total = data.get('total', 0)
        self.shipping_address = data.get('shipping_address')
        self.status = data.get('status', 'pending')
        self.payment_method = data.get('payment_method')
        self.created_at = data.get('created_at', datetime.utcnow())
        self.updated_at = data.get('updated_at', datetime.utcnow())
        raw_items = data.get('items', [])
        self.items = [OrderItem(item) if isinstance(item, dict) else item for item in raw_items]
        self._user = None
    
    def update_status(self, new_status):
        self.status = new_status
        self.updated_at = datetime.utcnow()
    
    @property
    def user(self):
        if self._user is None and self.user_id:
            from mongo_db import MongoUserRepo
            self._user = MongoUserRepo.find_by_id(self.user_id)
        return self._user
    
    @user.setter
    def user(self, value):
        self._user = value
    
    def to_dict(self):
        return {
            'user_id': self.user_id,
            'total': self.total,
            'shipping_address': self.shipping_address,
            'status': self.status,
            'payment_method': self.payment_method,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'items': [{'product_id': i.product_id, 'name': i.name, 'quantity': i.quantity, 'price': i.price} for i in self.items]
        }
    
    @classmethod
    def from_doc(cls, doc):
        if doc is None:
            return None
        return cls(doc)


class MongoReview:
    collection_name = 'reviews'
    
    def __init__(self, data):
        self._id = data.get('_id')
        self.id = str(data.get('_id')) if data.get('_id') else None
        self.product_id = data.get('product_id')
        self.user_id = data.get('user_id')
        self.rating = data.get('rating', 0)
        self.comment = data.get('comment')
        self.created_at = data.get('created_at', datetime.utcnow())
        self.user = None
    
    def to_dict(self):
        return {
            'product_id': self.product_id,
            'user_id': self.user_id,
            'rating': self.rating,
            'comment': self.comment,
            'created_at': self.created_at
        }
    
    @classmethod
    def from_doc(cls, doc):
        if doc is None:
            return None
        return cls(doc)


class MongoAddress:
    collection_name = 'addresses'
    
    def __init__(self, data):
        self._id = data.get('_id')
        self.id = str(data.get('_id')) if data.get('_id') else None
        self.user_id = data.get('user_id')
        self.name = data.get('name')
        self.street = data.get('street')
        self.city = data.get('city')
        self.state = data.get('state')
        self.zip_code = data.get('zip_code')
        self.phone = data.get('phone')
        self.created_at = data.get('created_at', datetime.utcnow())
    
    def to_dict(self):
        return {
            'user_id': self.user_id,
            'name': self.name,
            'street': self.street,
            'city': self.city,
            'state': self.state,
            'zip_code': self.zip_code,
            'phone': self.phone,
            'created_at': self.created_at
        }
    
    @classmethod
    def from_doc(cls, doc):
        if doc is None:
            return None
        return cls(doc)


class MongoVisitorLog:
    collection_name = 'visitor_logs'
    
    def __init__(self, data):
        self._id = data.get('_id')
        self.id = str(data.get('_id')) if data.get('_id') else None
        self.ip_address = data.get('ip_address')
        self.user_agent = data.get('user_agent')
        self.page = data.get('page')
        self.timestamp = data.get('timestamp', datetime.utcnow())
    
    def to_dict(self):
        return {
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'page': self.page,
            'timestamp': self.timestamp
        }
    
    @classmethod
    def from_doc(cls, doc):
        if doc is None:
            return None
        return cls(doc)


class MongoOTPCode:
    collection_name = 'otp_codes'
    
    def __init__(self, data):
        self._id = data.get('_id')
        self.id = str(data.get('_id')) if data.get('_id') else None
        self.email = data.get('email')
        self.purpose = data.get('purpose')
        self.otp = data.get('otp')
        self.attempts = data.get('attempts', 0)
        self.created_at = data.get('created_at', datetime.utcnow())
        self.expires_at = data.get('expires_at')
    
    def to_dict(self):
        return {
            'email': self.email,
            'purpose': self.purpose,
            'otp': self.otp,
            'attempts': self.attempts,
            'created_at': self.created_at,
            'expires_at': self.expires_at
        }
    
    @classmethod
    def from_doc(cls, doc):
        if doc is None:
            return None
        return cls(doc)


class CartItem:
    def __init__(self, product_id, quantity, price):
        self.product_id = product_id
        self.quantity = int(quantity)
        self.price = float(price)
    
    def get_total(self):
        return self.quantity * self.price
