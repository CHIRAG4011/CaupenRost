"""
MongoDB Database Layer for CaupenRost
This module provides MongoDB repository classes that mirror the SQLAlchemy repos.
"""
from datetime import datetime, timedelta
from bson import ObjectId
import os
import logging

_mongo_client = None
_mongo_db = None


def get_mongo_db():
    """Get or create MongoDB connection"""
    global _mongo_client, _mongo_db
    
    if _mongo_db is not None:
        return _mongo_db
    
    mongo_uri = (
        os.environ.get('MONGO_URI') or
        (os.environ.get('DATABASE_URL') if os.environ.get('DATABASE_URL') and 'mongodb' in os.environ.get('DATABASE_URL', '') else None) or
        'mongodb://localhost:27017/caupenrost'
    )
    
    try:
        from pymongo import MongoClient
        _mongo_client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        _mongo_client.server_info()
        
        db_name = mongo_uri.split('/')[-1].split('?')[0] or 'caupenrost'
        _mongo_db = _mongo_client[db_name]
        logging.info(f"Connected to MongoDB database: {db_name}")
        return _mongo_db
    except Exception as e:
        logging.error(f"Failed to connect to MongoDB: {e}")
        raise


def is_mongo_configured():
    """Check if MongoDB is configured"""
    return bool(os.environ.get('MONGO_URI'))


class MongoUserRepo:
    @staticmethod
    def _get_collection():
        return get_mongo_db()['users']
    
    @staticmethod
    def find_by_id(user_id):
        from mongodb_models import MongoUser
        try:
            doc = MongoUserRepo._get_collection().find_one({'_id': ObjectId(str(user_id))})
            return MongoUser.from_doc(doc)
        except:
            return None
    
    @staticmethod
    def find_by_username(username):
        from mongodb_models import MongoUser
        doc = MongoUserRepo._get_collection().find_one({'username': username})
        return MongoUser.from_doc(doc)
    
    @staticmethod
    def find_by_email(email):
        from mongodb_models import MongoUser
        doc = MongoUserRepo._get_collection().find_one({'email': email})
        return MongoUser.from_doc(doc)
    
    @staticmethod
    def find_by_username_or_email(value):
        from mongodb_models import MongoUser
        doc = MongoUserRepo._get_collection().find_one({
            '$or': [{'username': value}, {'email': value}]
        })
        return MongoUser.from_doc(doc)
    
    @staticmethod
    def exists_by_username_or_email(username, email):
        doc = MongoUserRepo._get_collection().find_one({
            '$or': [{'username': username}, {'email': email}]
        })
        return doc is not None
    
    @staticmethod
    def create(user_data):
        from mongodb_models import MongoUser
        doc = {
            'username': user_data.get('username'),
            'email': user_data.get('email'),
            'password_hash': user_data.get('password_hash'),
            'is_admin': user_data.get('is_admin', False),
            'created_at': datetime.utcnow()
        }
        result = MongoUserRepo._get_collection().insert_one(doc)
        doc['_id'] = result.inserted_id
        return MongoUser.from_doc(doc)
    
    @staticmethod
    def update(user_id, update_data):
        try:
            MongoUserRepo._get_collection().update_one(
                {'_id': ObjectId(str(user_id))},
                {'$set': update_data}
            )
        except:
            pass
    
    @staticmethod
    def find_all():
        from mongodb_models import MongoUser
        docs = MongoUserRepo._get_collection().find()
        return [MongoUser.from_doc(doc) for doc in docs]
    
    @staticmethod
    def count():
        return MongoUserRepo._get_collection().count_documents({})


class MongoCategoryRepo:
    @staticmethod
    def _get_collection():
        return get_mongo_db()['categories']
    
    @staticmethod
    def find_by_id(category_id):
        from mongodb_models import MongoCategory
        try:
            doc = MongoCategoryRepo._get_collection().find_one({'_id': ObjectId(str(category_id))})
            return MongoCategory.from_doc(doc)
        except:
            return None
    
    @staticmethod
    def find_by_name(name):
        from mongodb_models import MongoCategory
        doc = MongoCategoryRepo._get_collection().find_one({'name': name})
        return MongoCategory.from_doc(doc)
    
    @staticmethod
    def find_all():
        from mongodb_models import MongoCategory
        docs = MongoCategoryRepo._get_collection().find()
        return [MongoCategory.from_doc(doc) for doc in docs]
    
    @staticmethod
    def find_active():
        from mongodb_models import MongoCategory
        docs = MongoCategoryRepo._get_collection().find({'is_active': True})
        return [MongoCategory.from_doc(doc) for doc in docs]
    
    @staticmethod
    def create(category_data):
        from mongodb_models import MongoCategory
        doc = {
            'name': category_data.get('name'),
            'description': category_data.get('description', ''),
            'image_url': category_data.get('image_url', ''),
            'is_active': category_data.get('is_active', True),
            'created_at': datetime.utcnow()
        }
        result = MongoCategoryRepo._get_collection().insert_one(doc)
        doc['_id'] = result.inserted_id
        return MongoCategory.from_doc(doc)
    
    @staticmethod
    def update(category_id, update_data):
        try:
            MongoCategoryRepo._get_collection().update_one(
                {'_id': ObjectId(str(category_id))},
                {'$set': update_data}
            )
        except:
            pass
    
    @staticmethod
    def delete(category_id):
        try:
            MongoCategoryRepo._get_collection().delete_one({'_id': ObjectId(str(category_id))})
        except:
            pass
    
    @staticmethod
    def count():
        return MongoCategoryRepo._get_collection().count_documents({})
    
    @staticmethod
    def exists_by_name_exclude(name, exclude_id):
        """Check if category with name exists, excluding a specific ID"""
        query = {'name': {'$regex': f'^{name}$', '$options': 'i'}}
        if exclude_id:
            try:
                query['_id'] = {'$ne': ObjectId(str(exclude_id))}
            except:
                pass
        return MongoCategoryRepo._get_collection().find_one(query) is not None


class MongoProductRepo:
    @staticmethod
    def _get_collection():
        return get_mongo_db()['products']
    
    @staticmethod
    def _load_reviews(product):
        """Load reviews for a product and wrap in ReviewsList for template compatibility"""
        from mongodb_models import ReviewsList
        if product:
            reviews = MongoReviewRepo.find_by_product(product.id)
            product.reviews = ReviewsList(reviews if reviews else [])
        return product
    
    @staticmethod
    def find_by_id(product_id):
        from mongodb_models import MongoProduct
        try:
            doc = MongoProductRepo._get_collection().find_one({'_id': ObjectId(str(product_id))})
            product = MongoProduct.from_doc(doc)
            return MongoProductRepo._load_reviews(product)
        except:
            return None
    
    @staticmethod
    def find_all():
        from mongodb_models import MongoProduct
        docs = MongoProductRepo._get_collection().find()
        products = []
        for doc in docs:
            product = MongoProduct.from_doc(doc)
            products.append(MongoProductRepo._load_reviews(product))
        return products
    
    @staticmethod
    def find_by_category(category):
        from mongodb_models import MongoProduct
        docs = MongoProductRepo._get_collection().find({'category': category})
        products = []
        for doc in docs:
            product = MongoProduct.from_doc(doc)
            products.append(MongoProductRepo._load_reviews(product))
        return products
    
    @staticmethod
    def search(query, category=None):
        from mongodb_models import MongoProduct
        filter_query = {
            '$or': [
                {'name': {'$regex': query, '$options': 'i'}},
                {'description': {'$regex': query, '$options': 'i'}}
            ]
        }
        if category and category != 'all':
            filter_query['category'] = {'$regex': category, '$options': 'i'}
        
        docs = MongoProductRepo._get_collection().find(filter_query)
        products = []
        for doc in docs:
            product = MongoProduct.from_doc(doc)
            products.append(MongoProductRepo._load_reviews(product))
        return products
    
    @staticmethod
    def create(product_data):
        from mongodb_models import MongoProduct, ReviewsList
        doc = {
            'name': product_data.get('name'),
            'description': product_data.get('description'),
            'price': float(product_data.get('price', 0)),
            'category': product_data.get('category'),
            'category_id': product_data.get('category_id'),
            'image_url': product_data.get('image_url'),
            'stock': int(product_data.get('stock', 0)),
            'created_at': datetime.utcnow()
        }
        result = MongoProductRepo._get_collection().insert_one(doc)
        doc['_id'] = result.inserted_id
        product = MongoProduct.from_doc(doc)
        product.reviews = ReviewsList()
        return product
    
    @staticmethod
    def update(product_id, update_data):
        try:
            if 'price' in update_data:
                update_data['price'] = float(update_data['price'])
            if 'stock' in update_data:
                update_data['stock'] = int(update_data['stock'])
            MongoProductRepo._get_collection().update_one(
                {'_id': ObjectId(str(product_id))},
                {'$set': update_data}
            )
        except:
            pass
    
    @staticmethod
    def delete(product_id):
        try:
            MongoProductRepo._get_collection().delete_one({'_id': ObjectId(str(product_id))})
            MongoReviewRepo.delete_by_product(product_id)
        except:
            pass
    
    @staticmethod
    def find_limit(limit):
        from mongodb_models import MongoProduct
        docs = MongoProductRepo._get_collection().find().limit(limit)
        products = []
        for doc in docs:
            product = MongoProduct.from_doc(doc)
            products.append(MongoProductRepo._load_reviews(product))
        return products
    
    @staticmethod
    def count():
        return MongoProductRepo._get_collection().count_documents({})


class MongoOrderRepo:
    @staticmethod
    def _get_collection():
        return get_mongo_db()['orders']
    
    @staticmethod
    def find_by_id(order_id):
        from mongodb_models import MongoOrder
        try:
            doc = MongoOrderRepo._get_collection().find_one({'_id': ObjectId(str(order_id))})
            return MongoOrder.from_doc(doc)
        except:
            return None
    
    @staticmethod
    def find_by_user(user_id):
        from mongodb_models import MongoOrder
        docs = MongoOrderRepo._get_collection().find({'user_id': str(user_id)}).sort('created_at', -1)
        return [MongoOrder.from_doc(doc) for doc in docs]
    
    @staticmethod
    def find_all(sort_desc=True):
        from mongodb_models import MongoOrder
        sort_order = -1 if sort_desc else 1
        docs = MongoOrderRepo._get_collection().find().sort('created_at', sort_order)
        return [MongoOrder.from_doc(doc) for doc in docs]
    
    @staticmethod
    def create(order_data):
        from mongodb_models import MongoOrder
        doc = {
            'user_id': str(order_data.get('user_id')),
            'total': float(order_data.get('total', 0)),
            'shipping_address': order_data.get('shipping_address'),
            'status': order_data.get('status', 'pending'),
            'payment_method': order_data.get('payment_method'),
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'items': order_data.get('items', [])
        }
        result = MongoOrderRepo._get_collection().insert_one(doc)
        doc['_id'] = result.inserted_id
        order = MongoOrder.from_doc(doc)
        order.user = MongoUserRepo.find_by_id(order.user_id)
        return order
    
    @staticmethod
    def update(order_id, update_data):
        try:
            update_data['updated_at'] = datetime.utcnow()
            MongoOrderRepo._get_collection().update_one(
                {'_id': ObjectId(str(order_id))},
                {'$set': update_data}
            )
        except:
            pass
    
    @staticmethod
    def count():
        return MongoOrderRepo._get_collection().count_documents({})
    
    @staticmethod
    def count_by_status(status):
        return MongoOrderRepo._get_collection().count_documents({'status': status})
    
    @staticmethod
    def sum_total():
        pipeline = [{'$group': {'_id': None, 'total': {'$sum': '$total'}}}]
        result = list(MongoOrderRepo._get_collection().aggregate(pipeline))
        return result[0]['total'] if result else 0
    
    @staticmethod
    def find_recent(limit=10):
        """Find most recent orders"""
        from mongodb_models import MongoOrder
        docs = MongoOrderRepo._get_collection().find().sort('created_at', -1).limit(limit)
        return [MongoOrder.from_doc(doc) for doc in docs]


class MongoReviewRepo:
    @staticmethod
    def _get_collection():
        return get_mongo_db()['reviews']
    
    @staticmethod
    def find_by_product(product_id):
        from mongodb_models import MongoReview
        docs = MongoReviewRepo._get_collection().find({'product_id': str(product_id)})
        reviews = []
        for doc in docs:
            review = MongoReview.from_doc(doc)
            if review:
                review.user = MongoUserRepo.find_by_id(review.user_id)
            reviews.append(review)
        return reviews
    
    @staticmethod
    def create(review_data):
        from mongodb_models import MongoReview
        doc = {
            'product_id': str(review_data.get('product_id')),
            'user_id': str(review_data.get('user_id')),
            'rating': int(review_data.get('rating', 0)),
            'comment': review_data.get('comment'),
            'created_at': datetime.utcnow()
        }
        result = MongoReviewRepo._get_collection().insert_one(doc)
        doc['_id'] = result.inserted_id
        review = MongoReview.from_doc(doc)
        review.user = MongoUserRepo.find_by_id(review.user_id)
        return review
    
    @staticmethod
    def delete_by_product(product_id):
        return MongoReviewRepo._get_collection().delete_many({'product_id': str(product_id)}).deleted_count
    
    @staticmethod
    def count():
        return MongoReviewRepo._get_collection().count_documents({})


class MongoAddressRepo:
    @staticmethod
    def _get_collection():
        return get_mongo_db()['addresses']
    
    @staticmethod
    def find_by_id(address_id):
        from mongodb_models import MongoAddress
        try:
            doc = MongoAddressRepo._get_collection().find_one({'_id': ObjectId(str(address_id))})
            return MongoAddress.from_doc(doc)
        except:
            return None
    
    @staticmethod
    def find_by_user(user_id):
        from mongodb_models import MongoAddress
        docs = MongoAddressRepo._get_collection().find({'user_id': str(user_id)})
        return [MongoAddress.from_doc(doc) for doc in docs]
    
    @staticmethod
    def create(address_data):
        from mongodb_models import MongoAddress
        doc = {
            'user_id': str(address_data.get('user_id')),
            'name': address_data.get('name'),
            'street': address_data.get('street'),
            'city': address_data.get('city'),
            'state': address_data.get('state'),
            'zip_code': address_data.get('zip_code'),
            'phone': address_data.get('phone'),
            'created_at': datetime.utcnow()
        }
        result = MongoAddressRepo._get_collection().insert_one(doc)
        doc['_id'] = result.inserted_id
        return MongoAddress.from_doc(doc)
    
    @staticmethod
    def count():
        return MongoAddressRepo._get_collection().count_documents({})


class MongoVisitorLogRepo:
    @staticmethod
    def _get_collection():
        return get_mongo_db()['visitor_logs']
    
    @staticmethod
    def create(log_data):
        doc = {
            'ip_address': log_data.get('ip_address'),
            'user_agent': log_data.get('user_agent'),
            'page': log_data.get('page'),
            'timestamp': datetime.utcnow()
        }
        MongoVisitorLogRepo._get_collection().insert_one(doc)
    
    @staticmethod
    def count_daily():
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        pipeline = [
            {'$match': {'timestamp': {'$gte': today}}},
            {'$group': {'_id': '$ip_address'}},
            {'$count': 'count'}
        ]
        result = list(MongoVisitorLogRepo._get_collection().aggregate(pipeline))
        return result[0]['count'] if result else 0
    
    @staticmethod
    def get_weekly_data():
        weekly_data = {}
        for i in range(7):
            date = datetime.utcnow() - timedelta(days=6-i)
            start = date.replace(hour=0, minute=0, second=0, microsecond=0)
            end = start + timedelta(days=1)
            
            pipeline = [
                {'$match': {'timestamp': {'$gte': start, '$lt': end}}},
                {'$group': {'_id': '$ip_address'}},
                {'$count': 'count'}
            ]
            result = list(MongoVisitorLogRepo._get_collection().aggregate(pipeline))
            weekly_data[start.strftime('%Y-%m-%d')] = result[0]['count'] if result else 0
        
        return weekly_data


class MongoOTPRepo:
    @staticmethod
    def _get_collection():
        return get_mongo_db()['otp_codes']
    
    @staticmethod
    def find_by_email_purpose(email, purpose):
        from mongodb_models import MongoOTPCode
        doc = MongoOTPRepo._get_collection().find_one({'email': email, 'purpose': purpose})
        return MongoOTPCode.from_doc(doc)
    
    @staticmethod
    def create(otp_data):
        from mongodb_models import MongoOTPCode
        doc = {
            'email': otp_data.get('email'),
            'purpose': otp_data.get('purpose'),
            'otp': otp_data.get('otp'),
            'attempts': otp_data.get('attempts', 0),
            'created_at': datetime.utcnow(),
            'expires_at': otp_data.get('expires_at')
        }
        result = MongoOTPRepo._get_collection().insert_one(doc)
        doc['_id'] = result.inserted_id
        return MongoOTPCode.from_doc(doc)
    
    @staticmethod
    def delete_by_email_purpose(email, purpose):
        MongoOTPRepo._get_collection().delete_many({'email': email, 'purpose': purpose})
    
    @staticmethod
    def update(otp_id, update_data):
        try:
            MongoOTPRepo._get_collection().update_one(
                {'_id': ObjectId(str(otp_id))},
                {'$set': update_data}
            )
        except:
            pass
    
    @staticmethod
    def delete(otp_id):
        try:
            MongoOTPRepo._get_collection().delete_one({'_id': ObjectId(str(otp_id))})
        except:
            pass


class MongoTicketRepo:
    @staticmethod
    def _get_collection():
        return get_mongo_db()['tickets']
    
    @staticmethod
    def find_by_id(ticket_id):
        from mongodb_models import MongoTicket
        try:
            doc = MongoTicketRepo._get_collection().find_one({'_id': ObjectId(str(ticket_id))})
            ticket = MongoTicket.from_doc(doc)
            if ticket:
                ticket.messages = MongoTicketMessageRepo.find_by_ticket(ticket_id)
            return ticket
        except:
            return None
    
    @staticmethod
    def find_by_user(user_id):
        from mongodb_models import MongoTicket
        docs = MongoTicketRepo._get_collection().find({'user_id': str(user_id)}).sort('created_at', -1)
        return [MongoTicket.from_doc(doc) for doc in docs]
    
    @staticmethod
    def find_all(status=None, ticket_type=None):
        from mongodb_models import MongoTicket
        query = {}
        if status:
            query['status'] = status
        if ticket_type:
            query['ticket_type'] = ticket_type
        docs = MongoTicketRepo._get_collection().find(query).sort('created_at', -1)
        return [MongoTicket.from_doc(doc) for doc in docs]
    
    @staticmethod
    def create(ticket_data):
        from mongodb_models import MongoTicket
        doc = {
            'user_id': str(ticket_data.get('user_id')),
            'order_id': str(ticket_data.get('order_id')) if ticket_data.get('order_id') else None,
            'ticket_type': ticket_data.get('ticket_type'),
            'subject': ticket_data.get('subject'),
            'description': ticket_data.get('description'),
            'status': ticket_data.get('status', 'open'),
            'priority': ticket_data.get('priority', 'normal'),
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        result = MongoTicketRepo._get_collection().insert_one(doc)
        doc['_id'] = result.inserted_id
        return MongoTicket.from_doc(doc)
    
    @staticmethod
    def update(ticket_id, update_data):
        try:
            update_data['updated_at'] = datetime.utcnow()
            MongoTicketRepo._get_collection().update_one(
                {'_id': ObjectId(str(ticket_id))},
                {'$set': update_data}
            )
        except:
            pass
    
    @staticmethod
    def count():
        return MongoTicketRepo._get_collection().count_documents({})
    
    @staticmethod
    def count_by_status(status):
        return MongoTicketRepo._get_collection().count_documents({'status': status})


class MongoTicketMessageRepo:
    @staticmethod
    def _get_collection():
        return get_mongo_db()['ticket_messages']
    
    @staticmethod
    def find_by_ticket(ticket_id):
        from mongodb_models import MongoTicketMessage
        docs = MongoTicketMessageRepo._get_collection().find({'ticket_id': str(ticket_id)}).sort('created_at', 1)
        messages = []
        for doc in docs:
            msg = MongoTicketMessage.from_doc(doc)
            if msg:
                msg.author = MongoUserRepo.find_by_id(msg.author_id)
            messages.append(msg)
        return messages
    
    @staticmethod
    def create(message_data):
        from mongodb_models import MongoTicketMessage
        doc = {
            'ticket_id': str(message_data.get('ticket_id')),
            'author_id': str(message_data.get('author_id')),
            'message': message_data.get('message'),
            'is_admin_reply': message_data.get('is_admin_reply', False),
            'created_at': datetime.utcnow()
        }
        result = MongoTicketMessageRepo._get_collection().insert_one(doc)
        doc['_id'] = result.inserted_id
        msg = MongoTicketMessage.from_doc(doc)
        msg.author = MongoUserRepo.find_by_id(msg.author_id)
        return msg


class MongoRoleRepo:
    SYSTEM_ROLES = [
        {'name': 'admin', 'description': 'Full access to all admin features', 'permissions': ['all'], 'is_system': True},
        {'name': 'manager', 'description': 'Manage orders, products and view analytics', 'permissions': ['orders', 'products', 'analytics'], 'is_system': True},
        {'name': 'staff', 'description': 'View and update orders only', 'permissions': ['orders'], 'is_system': True},
        {'name': 'customer', 'description': 'Regular customer account', 'permissions': [], 'is_system': True},
    ]

    @staticmethod
    def _get_collection():
        return get_mongo_db()['roles']

    @staticmethod
    def ensure_system_roles():
        from mongodb_models import MongoRole
        for role_data in MongoRoleRepo.SYSTEM_ROLES:
            existing = MongoRoleRepo._get_collection().find_one({'name': role_data['name']})
            if not existing:
                doc = {**role_data, 'created_at': datetime.utcnow()}
                MongoRoleRepo._get_collection().insert_one(doc)

    @staticmethod
    def find_all():
        from mongodb_models import MongoRole
        docs = MongoRoleRepo._get_collection().find().sort('name', 1)
        return [MongoRole.from_doc(doc) for doc in docs]

    @staticmethod
    def find_by_id(role_id):
        from mongodb_models import MongoRole
        try:
            doc = MongoRoleRepo._get_collection().find_one({'_id': ObjectId(str(role_id))})
            return MongoRole.from_doc(doc)
        except:
            return None

    @staticmethod
    def find_by_name(name):
        from mongodb_models import MongoRole
        doc = MongoRoleRepo._get_collection().find_one({'name': name})
        return MongoRole.from_doc(doc)

    @staticmethod
    def create(role_data):
        from mongodb_models import MongoRole
        doc = {
            'name': role_data.get('name'),
            'description': role_data.get('description', ''),
            'permissions': role_data.get('permissions', []),
            'is_system': False,
            'created_at': datetime.utcnow()
        }
        result = MongoRoleRepo._get_collection().insert_one(doc)
        doc['_id'] = result.inserted_id
        return MongoRole.from_doc(doc)

    @staticmethod
    def update(role_id, update_data):
        try:
            MongoRoleRepo._get_collection().update_one(
                {'_id': ObjectId(str(role_id))},
                {'$set': update_data}
            )
        except:
            pass

    @staticmethod
    def delete(role_id):
        try:
            MongoRoleRepo._get_collection().delete_one({'_id': ObjectId(str(role_id)), 'is_system': False})
        except:
            pass

    @staticmethod
    def count():
        return MongoRoleRepo._get_collection().count_documents({})


class MongoAnnouncementRepo:
    @staticmethod
    def _get_collection():
        return get_mongo_db()['announcements']

    @staticmethod
    def find_all():
        from mongodb_models import MongoAnnouncement
        docs = MongoAnnouncementRepo._get_collection().find().sort('priority', -1)
        return [MongoAnnouncement.from_doc(doc) for doc in docs]

    @staticmethod
    def find_active():
        from mongodb_models import MongoAnnouncement
        now = datetime.utcnow()
        query = {'is_active': True, '$or': [{'ends_at': None}, {'ends_at': {'$gt': now}}],
                 '$or': [{'starts_at': None}, {'starts_at': {'$lte': now}}]}
        docs = MongoAnnouncementRepo._get_collection().find({'is_active': True}).sort('priority', -1)
        return [MongoAnnouncement.from_doc(doc) for doc in docs]

    @staticmethod
    def find_by_id(ann_id):
        from mongodb_models import MongoAnnouncement
        try:
            doc = MongoAnnouncementRepo._get_collection().find_one({'_id': ObjectId(str(ann_id))})
            return MongoAnnouncement.from_doc(doc)
        except:
            return None

    @staticmethod
    def create(data):
        from mongodb_models import MongoAnnouncement
        doc = {
            'text': data.get('text', ''),
            'link_url': data.get('link_url', ''),
            'link_text': data.get('link_text', ''),
            'bg_color': data.get('bg_color', '#8B4513'),
            'text_color': data.get('text_color', '#ffffff'),
            'icon': data.get('icon', 'fas fa-bullhorn'),
            'is_active': data.get('is_active', True),
            'is_dismissible': data.get('is_dismissible', True),
            'priority': int(data.get('priority', 1)),
            'starts_at': data.get('starts_at'),
            'ends_at': data.get('ends_at'),
            'created_at': datetime.utcnow()
        }
        result = MongoAnnouncementRepo._get_collection().insert_one(doc)
        doc['_id'] = result.inserted_id
        return MongoAnnouncement.from_doc(doc)

    @staticmethod
    def update(ann_id, update_data):
        try:
            MongoAnnouncementRepo._get_collection().update_one(
                {'_id': ObjectId(str(ann_id))}, {'$set': update_data})
        except:
            pass

    @staticmethod
    def delete(ann_id):
        try:
            MongoAnnouncementRepo._get_collection().delete_one({'_id': ObjectId(str(ann_id))})
        except:
            pass

    @staticmethod
    def count():
        return MongoAnnouncementRepo._get_collection().count_documents({})


class MongoCouponRepo:
    @staticmethod
    def _get_collection():
        return get_mongo_db()['coupons']

    @staticmethod
    def find_all():
        from mongodb_models import MongoCoupon
        docs = MongoCouponRepo._get_collection().find().sort('created_at', -1)
        return [MongoCoupon.from_doc(doc) for doc in docs]

    @staticmethod
    def find_by_id(coupon_id):
        from mongodb_models import MongoCoupon
        try:
            doc = MongoCouponRepo._get_collection().find_one({'_id': ObjectId(str(coupon_id))})
            return MongoCoupon.from_doc(doc)
        except:
            return None

    @staticmethod
    def find_by_code(code):
        from mongodb_models import MongoCoupon
        doc = MongoCouponRepo._get_collection().find_one({'code': code.strip().upper()})
        return MongoCoupon.from_doc(doc)

    @staticmethod
    def create(data):
        from mongodb_models import MongoCoupon
        from datetime import timedelta
        expires_at = None
        if data.get('expires_at'):
            try:
                expires_at = datetime.strptime(data['expires_at'], '%Y-%m-%d')
            except:
                pass
        doc = {
            'code': data.get('code', '').strip().upper(),
            'description': data.get('description', ''),
            'discount_type': data.get('discount_type', 'percentage'),
            'discount_value': float(data.get('discount_value', 0)),
            'min_order_amount': float(data.get('min_order_amount', 0)),
            'max_discount': float(data.get('max_discount', 0)),
            'max_uses': int(data.get('max_uses', 0)),
            'uses_count': 0,
            'is_active': True,
            'expires_at': expires_at,
            'created_at': datetime.utcnow()
        }
        result = MongoCouponRepo._get_collection().insert_one(doc)
        doc['_id'] = result.inserted_id
        return MongoCoupon.from_doc(doc)

    @staticmethod
    def update(coupon_id, update_data):
        try:
            MongoCouponRepo._get_collection().update_one(
                {'_id': ObjectId(str(coupon_id))}, {'$set': update_data})
        except:
            pass

    @staticmethod
    def increment_uses(coupon_id):
        try:
            MongoCouponRepo._get_collection().update_one(
                {'_id': ObjectId(str(coupon_id))}, {'$inc': {'uses_count': 1}})
        except:
            pass

    @staticmethod
    def delete(coupon_id):
        try:
            MongoCouponRepo._get_collection().delete_one({'_id': ObjectId(str(coupon_id))})
        except:
            pass

    @staticmethod
    def count():
        return MongoCouponRepo._get_collection().count_documents({})


def setup_indexes():
    """Create MongoDB indexes for performance and TTL"""
    try:
        db = get_mongo_db()
        db['otp_codes'].create_index('expires_at', expireAfterSeconds=0)
        db['otp_codes'].create_index([('email', 1), ('purpose', 1)])
        db['visitor_logs'].create_index('timestamp')
        db['orders'].create_index([('user_id', 1), ('created_at', -1)])
        db['users'].create_index('email', unique=True)
        db['users'].create_index('username', unique=True)
        MongoRoleRepo.ensure_system_roles()
        logging.info("MongoDB indexes and system roles initialized")
    except Exception as e:
        logging.warning(f"Index setup warning: {e}")
