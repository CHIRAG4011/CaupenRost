from datetime import datetime
from werkzeug.security import check_password_hash, generate_password_hash
from bson import ObjectId


class ReviewsList(list):
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
        self.role = data.get('role', 'admin' if data.get('is_admin') else 'customer')
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
            'role': self.role,
            'created_at': self.created_at
        }

    @classmethod
    def from_doc(cls, doc):
        if doc is None:
            return None
        return cls(doc)


class MongoRole:
    collection_name = 'customroles'

    def __init__(self, data):
        self._id = data.get('_id')
        self.id = str(data.get('_id')) if data.get('_id') else None
        self.name = data.get('name')
        self.description = data.get('description', '')
        self.permissions = data.get('permissions', [])
        self.is_system = data.get('is_system', False)
        self.created_at = data.get('created_at', datetime.utcnow())

    def to_dict(self):
        return {
            'name': self.name,
            'description': self.description,
            'permissions': self.permissions,
            'is_system': self.is_system,
            'created_at': self.created_at
        }

    @classmethod
    def from_doc(cls, doc):
        if doc is None:
            return None
        return cls(doc)


class MongoCategory:
    collection_name = 'storecategory'

    def __init__(self, data):
        self._id = data.get('_id')
        self.id = str(data.get('_id')) if data.get('_id') else None
        self.name = data.get('name')
        self.description = data.get('description', '')
        self.image_url = data.get('image_url', '')
        self.is_active = data.get('is_active', True)
        self.created_at = data.get('created_at', datetime.utcnow())

    def get_product_count(self):
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
    collection_name = 'storeitems'

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
        self.is_available = data.get('is_available', True)
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
            'is_available': self.is_available,
            'created_at': self.created_at
        }

    @classmethod
    def from_doc(cls, doc):
        if doc is None:
            return None
        return cls(doc)


class OrderItem:
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
        self.payment_proof_url = data.get('payment_proof_url')
        self.payment_proof_uploaded_at = data.get('payment_proof_uploaded_at')
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
            'payment_proof_url': self.payment_proof_url,
            'payment_proof_uploaded_at': self.payment_proof_uploaded_at,
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
    collection_name = 'productreviews'

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
            'user_id': self.user_id, 'name': self.name, 'street': self.street,
            'city': self.city, 'state': self.state, 'zip_code': self.zip_code,
            'phone': self.phone, 'created_at': self.created_at
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
            'email': self.email, 'purpose': self.purpose, 'otp': self.otp,
            'attempts': self.attempts, 'created_at': self.created_at, 'expires_at': self.expires_at
        }

    @classmethod
    def from_doc(cls, doc):
        if doc is None:
            return None
        return cls(doc)


class MongoTicket:
    collection_name = 'tickets'

    def __init__(self, data):
        self._id = data.get('_id')
        self.id = str(data.get('_id')) if data.get('_id') else None
        self.user_id = data.get('user_id')
        self.order_id = data.get('order_id')
        self.ticket_type = data.get('ticket_type')
        self.subject = data.get('subject')
        self.description = data.get('description')
        self.status = data.get('status', 'open')
        self.priority = data.get('priority', 'normal')
        self.created_at = data.get('created_at', datetime.utcnow())
        self.updated_at = data.get('updated_at', datetime.utcnow())
        self._user = None
        self._order = None
        self._messages = []

    @property
    def user(self):
        if self._user is None and self.user_id:
            from mongo_db import MongoUserRepo
            self._user = MongoUserRepo.find_by_id(self.user_id)
        return self._user

    @user.setter
    def user(self, value):
        self._user = value

    @property
    def order(self):
        if self._order is None and self.order_id:
            from mongo_db import MongoOrderRepo
            self._order = MongoOrderRepo.find_by_id(self.order_id)
        return self._order

    @property
    def messages(self):
        return self._messages

    @messages.setter
    def messages(self, value):
        self._messages = value

    def get_status_badge_class(self):
        return {'open': 'bg-primary', 'in_progress': 'bg-warning', 'resolved': 'bg-success', 'closed': 'bg-secondary'}.get(self.status, 'bg-secondary')

    def get_priority_badge_class(self):
        return {'low': 'bg-info', 'normal': 'bg-secondary', 'high': 'bg-warning', 'urgent': 'bg-danger'}.get(self.priority, 'bg-secondary')

    def to_dict(self):
        return {
            'user_id': self.user_id, 'order_id': self.order_id, 'ticket_type': self.ticket_type,
            'subject': self.subject, 'description': self.description, 'status': self.status,
            'priority': self.priority, 'created_at': self.created_at, 'updated_at': self.updated_at
        }

    @classmethod
    def from_doc(cls, doc):
        if doc is None:
            return None
        return cls(doc)


class MongoTicketMessage:
    collection_name = 'ticketmessages'

    def __init__(self, data):
        self._id = data.get('_id')
        self.id = str(data.get('_id')) if data.get('_id') else None
        self.ticket_id = data.get('ticket_id')
        self.author_id = data.get('author_id')
        self.message = data.get('message')
        self.is_admin_reply = data.get('is_admin_reply', False)
        self.created_at = data.get('created_at', datetime.utcnow())
        self.author = None

    def to_dict(self):
        return {
            'ticket_id': self.ticket_id, 'author_id': self.author_id, 'message': self.message,
            'is_admin_reply': self.is_admin_reply, 'created_at': self.created_at
        }

    @classmethod
    def from_doc(cls, doc):
        if doc is None:
            return None
        return cls(doc)


class MongoAnnouncement:
    collection_name = 'announcements'

    def __init__(self, data):
        self._id = data.get('_id')
        self.id = str(data.get('_id')) if data.get('_id') else None
        self.text = data.get('text', '')
        self.link_url = data.get('link_url', '')
        self.link_text = data.get('link_text', '')
        self.bg_color = data.get('bg_color', '#8B4513')
        self.text_color = data.get('text_color', '#ffffff')
        self.icon = data.get('icon', 'fas fa-bullhorn')
        self.is_active = data.get('is_active', True)
        self.is_dismissible = data.get('is_dismissible', True)
        self.priority = data.get('priority', 1)
        self.starts_at = data.get('starts_at')
        self.ends_at = data.get('ends_at')
        self.created_at = data.get('created_at', datetime.utcnow())

    def to_dict(self):
        return {
            'text': self.text, 'link_url': self.link_url, 'link_text': self.link_text,
            'bg_color': self.bg_color, 'text_color': self.text_color, 'icon': self.icon,
            'is_active': self.is_active, 'is_dismissible': self.is_dismissible,
            'priority': self.priority, 'starts_at': self.starts_at, 'ends_at': self.ends_at,
            'created_at': self.created_at
        }

    @classmethod
    def from_doc(cls, doc):
        if doc is None:
            return None
        return cls(doc)


class MongoCoupon:
    collection_name = 'coupons'


class MongoPurchase:
    collection_name = 'purchases'

    def __init__(self, data):
        self._id = data.get('_id')
        self.id = str(data.get('_id')) if data.get('_id') else None
        self.user_id = data.get('user_id')
        self.total = data.get('total', 0)
        self.created_at = data.get('created_at', datetime.utcnow())

    def to_dict(self):
        return {
            'user_id': self.user_id,
            'total': self.total,
            'created_at': self.created_at
        }

    @classmethod
    def from_doc(cls, doc):
        if doc is None:
            return None
        return cls(doc)


class MongoSetting:
    collection_name = 'settings'

    def __init__(self, data):
        self._id = data.get('_id')
        self.id = str(data.get('_id')) if data.get('_id') else None
        self.key = data.get('key')
        self.value = data.get('value')
        self.created_at = data.get('created_at', datetime.utcnow())

    def to_dict(self):
        return {'key': self.key, 'value': self.value, 'created_at': self.created_at}

    @classmethod
    def from_doc(cls, doc):
        if doc is None:
            return None
        return cls(doc)


class MongoStoreCategory:
    collection_name = 'storecategories'

    def __init__(self, data):
        self._id = data.get('_id')
        self.id = str(data.get('_id')) if data.get('_id') else None
        self.name = data.get('name')
        self.slug = data.get('slug')
        self.created_at = data.get('created_at', datetime.utcnow())

    def to_dict(self):
        return {'name': self.name, 'slug': self.slug, 'created_at': self.created_at}

    @classmethod
    def from_doc(cls, doc):
        if doc is None:
            return None
        return cls(doc)


class MongoStoreItem:
    collection_name = 'storeitems'

    def __init__(self, data):
        self._id = data.get('_id')
        self.id = str(data.get('_id')) if data.get('_id') else None
        self.name = data.get('name')
        self.category_id = data.get('category_id')
        self.created_at = data.get('created_at', datetime.utcnow())

    def to_dict(self):
        return {'name': self.name, 'category_id': self.category_id, 'created_at': self.created_at}

    @classmethod
    def from_doc(cls, doc):
        if doc is None:
            return None
        return cls(doc)

    def __init__(self, data):
        self._id = data.get('_id')
        self.id = str(data.get('_id')) if data.get('_id') else None
        self.code = data.get('code', '').upper()
        self.description = data.get('description', '')
        self.discount_type = data.get('discount_type', 'percentage')
        self.discount_value = data.get('discount_value', 0)
        self.min_order_amount = data.get('min_order_amount', 0)
        self.max_discount = data.get('max_discount', 0)
        self.max_uses = data.get('max_uses', 0)
        self.uses_count = data.get('uses_count', 0)
        self.is_active = data.get('is_active', True)
        self.expires_at = data.get('expires_at')
        self.created_at = data.get('created_at', datetime.utcnow())

    def is_valid(self, cart_total):
        """Check if coupon is valid for a given cart total"""
        if not self.is_active:
            return False, "This coupon is inactive."
        if self.expires_at and datetime.utcnow() > self.expires_at:
            return False, "This coupon has expired."
        if self.max_uses > 0 and self.uses_count >= self.max_uses:
            return False, "This coupon has reached its usage limit."
        if cart_total < self.min_order_amount:
            return False, f"Minimum order amount of ₹{self.min_order_amount:.0f} required."
        return True, "Valid"

    def calculate_discount(self, cart_total):
        """Calculate discount amount"""
        if self.discount_type == 'percentage':
            discount = cart_total * (self.discount_value / 100)
            if self.max_discount > 0:
                discount = min(discount, self.max_discount)
        else:
            discount = min(self.discount_value, cart_total)
        return round(discount, 2)

    def to_dict(self):
        return {
            'code': self.code, 'description': self.description,
            'discount_type': self.discount_type, 'discount_value': self.discount_value,
            'min_order_amount': self.min_order_amount, 'max_discount': self.max_discount,
            'max_uses': self.max_uses, 'uses_count': self.uses_count,
            'is_active': self.is_active, 'expires_at': self.expires_at,
            'created_at': self.created_at
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
