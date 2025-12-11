from bson import ObjectId
from datetime import datetime
from mongodb_models import (
    MongoUser, MongoCategory, MongoProduct, MongoOrder, 
    MongoReview, MongoAddress, MongoVisitorLog, MongoOTPCode
)


def get_db():
    from app import mongo
    return mongo.db


class UserRepo:
    @staticmethod
    def find_by_id(user_id):
        db = get_db()
        try:
            doc = db.users.find_one({'_id': ObjectId(user_id)})
            return MongoUser.from_doc(doc)
        except:
            return None
    
    @staticmethod
    def find_by_username(username):
        db = get_db()
        doc = db.users.find_one({'username': username})
        return MongoUser.from_doc(doc)
    
    @staticmethod
    def find_by_email(email):
        db = get_db()
        doc = db.users.find_one({'email': email})
        return MongoUser.from_doc(doc)
    
    @staticmethod
    def find_by_username_or_email(value):
        db = get_db()
        doc = db.users.find_one({'$or': [{'username': value}, {'email': value}]})
        return MongoUser.from_doc(doc)
    
    @staticmethod
    def exists_by_username_or_email(username, email):
        db = get_db()
        doc = db.users.find_one({'$or': [{'username': username}, {'email': email}]})
        return doc is not None
    
    @staticmethod
    def create(user_data):
        db = get_db()
        user_data['created_at'] = datetime.utcnow()
        result = db.users.insert_one(user_data)
        user_data['_id'] = result.inserted_id
        return MongoUser.from_doc(user_data)
    
    @staticmethod
    def update(user_id, update_data):
        db = get_db()
        db.users.update_one({'_id': ObjectId(user_id)}, {'$set': update_data})
    
    @staticmethod
    def find_all():
        db = get_db()
        docs = db.users.find()
        return [MongoUser.from_doc(doc) for doc in docs]
    
    @staticmethod
    def count():
        db = get_db()
        return db.users.count_documents({})


class CategoryRepo:
    @staticmethod
    def find_by_id(category_id):
        db = get_db()
        try:
            doc = db.categories.find_one({'_id': ObjectId(category_id)})
            return MongoCategory.from_doc(doc)
        except:
            return None
    
    @staticmethod
    def find_by_name(name):
        db = get_db()
        doc = db.categories.find_one({'name': name})
        return MongoCategory.from_doc(doc)
    
    @staticmethod
    def find_active():
        db = get_db()
        docs = db.categories.find({'is_active': True})
        return [MongoCategory.from_doc(doc) for doc in docs]
    
    @staticmethod
    def find_all():
        db = get_db()
        docs = db.categories.find()
        return [MongoCategory.from_doc(doc) for doc in docs]
    
    @staticmethod
    def create(category_data):
        db = get_db()
        category_data['created_at'] = datetime.utcnow()
        category_data['is_active'] = category_data.get('is_active', True)
        result = db.categories.insert_one(category_data)
        category_data['_id'] = result.inserted_id
        return MongoCategory.from_doc(category_data)
    
    @staticmethod
    def update(category_id, update_data):
        db = get_db()
        db.categories.update_one({'_id': ObjectId(category_id)}, {'$set': update_data})
    
    @staticmethod
    def delete(category_id):
        db = get_db()
        db.categories.delete_one({'_id': ObjectId(category_id)})
    
    @staticmethod
    def exists_by_name_exclude(name, exclude_id):
        db = get_db()
        query = {'name': {'$regex': f'^{name}$', '$options': 'i'}}
        if exclude_id:
            query['_id'] = {'$ne': ObjectId(exclude_id)}
        doc = db.categories.find_one(query)
        return doc is not None
    
    @staticmethod
    def count():
        db = get_db()
        return db.categories.count_documents({})


class ProductRepo:
    @staticmethod
    def find_by_id(product_id):
        db = get_db()
        try:
            doc = db.products.find_one({'_id': ObjectId(product_id)})
            return MongoProduct.from_doc(doc)
        except:
            return None
    
    @staticmethod
    def find_all():
        db = get_db()
        docs = db.products.find()
        return [MongoProduct.from_doc(doc) for doc in docs]
    
    @staticmethod
    def find_by_category(category_name):
        db = get_db()
        docs = db.products.find({'category': category_name})
        return [MongoProduct.from_doc(doc) for doc in docs]
    
    @staticmethod
    def find_limit(limit):
        db = get_db()
        docs = db.products.find().limit(limit)
        return [MongoProduct.from_doc(doc) for doc in docs]
    
    @staticmethod
    def search(query, category=None):
        db = get_db()
        filter_query = {}
        
        if category and category != 'all':
            filter_query['category'] = {'$regex': category, '$options': 'i'}
        
        if query:
            filter_query['$or'] = [
                {'name': {'$regex': query, '$options': 'i'}},
                {'description': {'$regex': query, '$options': 'i'}}
            ]
        
        docs = db.products.find(filter_query)
        return [MongoProduct.from_doc(doc) for doc in docs]
    
    @staticmethod
    def create(product_data):
        db = get_db()
        product_data['created_at'] = datetime.utcnow()
        result = db.products.insert_one(product_data)
        product_data['_id'] = result.inserted_id
        return MongoProduct.from_doc(product_data)
    
    @staticmethod
    def update(product_id, update_data):
        db = get_db()
        db.products.update_one({'_id': ObjectId(product_id)}, {'$set': update_data})
    
    @staticmethod
    def delete(product_id):
        db = get_db()
        db.products.delete_one({'_id': ObjectId(product_id)})
    
    @staticmethod
    def count():
        db = get_db()
        return db.products.count_documents({})


class OrderRepo:
    @staticmethod
    def find_by_id(order_id):
        db = get_db()
        try:
            doc = db.orders.find_one({'_id': ObjectId(order_id)})
            return MongoOrder.from_doc(doc)
        except:
            return None
    
    @staticmethod
    def find_by_user(user_id, sort_desc=True):
        db = get_db()
        sort_order = -1 if sort_desc else 1
        docs = db.orders.find({'user_id': user_id}).sort('created_at', sort_order)
        return [MongoOrder.from_doc(doc) for doc in docs]
    
    @staticmethod
    def find_all(sort_desc=True):
        db = get_db()
        sort_order = -1 if sort_desc else 1
        docs = db.orders.find().sort('created_at', sort_order)
        return [MongoOrder.from_doc(doc) for doc in docs]
    
    @staticmethod
    def find_recent(limit=10):
        db = get_db()
        docs = db.orders.find().sort('created_at', -1).limit(limit)
        return [MongoOrder.from_doc(doc) for doc in docs]
    
    @staticmethod
    def create(order_data):
        db = get_db()
        order_data['created_at'] = datetime.utcnow()
        order_data['updated_at'] = datetime.utcnow()
        result = db.orders.insert_one(order_data)
        order_data['_id'] = result.inserted_id
        return MongoOrder.from_doc(order_data)
    
    @staticmethod
    def update(order_id, update_data):
        db = get_db()
        update_data['updated_at'] = datetime.utcnow()
        db.orders.update_one({'_id': ObjectId(order_id)}, {'$set': update_data})
    
    @staticmethod
    def count():
        db = get_db()
        return db.orders.count_documents({})
    
    @staticmethod
    def count_by_status(status):
        db = get_db()
        return db.orders.count_documents({'status': status})
    
    @staticmethod
    def sum_total():
        db = get_db()
        pipeline = [{'$group': {'_id': None, 'total': {'$sum': '$total'}}}]
        result = list(db.orders.aggregate(pipeline))
        return result[0]['total'] if result else 0


class ReviewRepo:
    @staticmethod
    def find_by_product(product_id):
        db = get_db()
        docs = db.reviews.find({'product_id': product_id})
        return [MongoReview.from_doc(doc) for doc in docs]
    
    @staticmethod
    def create(review_data):
        db = get_db()
        review_data['created_at'] = datetime.utcnow()
        result = db.reviews.insert_one(review_data)
        review_data['_id'] = result.inserted_id
        return MongoReview.from_doc(review_data)
    
    @staticmethod
    def delete_by_product(product_id):
        db = get_db()
        result = db.reviews.delete_many({'product_id': product_id})
        return result.deleted_count


class AddressRepo:
    @staticmethod
    def find_by_id(address_id):
        db = get_db()
        try:
            doc = db.addresses.find_one({'_id': ObjectId(address_id)})
            return MongoAddress.from_doc(doc)
        except:
            return None
    
    @staticmethod
    def find_by_user(user_id):
        db = get_db()
        docs = db.addresses.find({'user_id': user_id})
        return [MongoAddress.from_doc(doc) for doc in docs]
    
    @staticmethod
    def create(address_data):
        db = get_db()
        address_data['created_at'] = datetime.utcnow()
        result = db.addresses.insert_one(address_data)
        address_data['_id'] = result.inserted_id
        return MongoAddress.from_doc(address_data)


class VisitorLogRepo:
    @staticmethod
    def create(log_data):
        db = get_db()
        log_data['timestamp'] = datetime.utcnow()
        db.visitor_logs.insert_one(log_data)
    
    @staticmethod
    def count_daily():
        db = get_db()
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        pipeline = [
            {'$match': {'timestamp': {'$gte': today}}},
            {'$group': {'_id': '$ip_address'}},
            {'$count': 'count'}
        ]
        result = list(db.visitor_logs.aggregate(pipeline))
        return result[0]['count'] if result else 0
    
    @staticmethod
    def get_weekly_data():
        from datetime import timedelta
        db = get_db()
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
            result = list(db.visitor_logs.aggregate(pipeline))
            count = result[0]['count'] if result else 0
            weekly_data[start.strftime('%Y-%m-%d')] = count
        
        return weekly_data


class OTPRepo:
    @staticmethod
    def find_by_email_purpose(email, purpose):
        db = get_db()
        doc = db.otp_codes.find_one({'email': email, 'purpose': purpose})
        return MongoOTPCode.from_doc(doc)
    
    @staticmethod
    def delete_by_email_purpose(email, purpose):
        db = get_db()
        db.otp_codes.delete_many({'email': email, 'purpose': purpose})
    
    @staticmethod
    def create(otp_data):
        db = get_db()
        otp_data['created_at'] = datetime.utcnow()
        result = db.otp_codes.insert_one(otp_data)
        otp_data['_id'] = result.inserted_id
        return MongoOTPCode.from_doc(otp_data)
    
    @staticmethod
    def update(otp_id, update_data):
        db = get_db()
        db.otp_codes.update_one({'_id': ObjectId(otp_id)}, {'$set': update_data})
    
    @staticmethod
    def delete(otp_id):
        db = get_db()
        db.otp_codes.delete_one({'_id': ObjectId(otp_id)})
