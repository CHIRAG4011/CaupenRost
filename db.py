from datetime import datetime, timedelta
from sqlalchemy import func, or_


def get_db():
    from app import db
    return db


class UserRepo:
    @staticmethod
    def find_by_id(user_id):
        from models import User
        db = get_db()
        try:
            return db.session.get(User, int(user_id))
        except (ValueError, TypeError):
            return None
    
    @staticmethod
    def find_by_username(username):
        from models import User
        return User.query.filter_by(username=username).first()
    
    @staticmethod
    def find_by_email(email):
        from models import User
        return User.query.filter_by(email=email).first()
    
    @staticmethod
    def find_by_username_or_email(value):
        from models import User
        return User.query.filter(
            or_(User.username == value, User.email == value)
        ).first()
    
    @staticmethod
    def exists_by_username_or_email(username, email):
        from models import User
        return User.query.filter(
            or_(User.username == username, User.email == email)
        ).first() is not None
    
    @staticmethod
    def create(user_data):
        from models import User
        db = get_db()
        user = User(
            username=user_data.get('username'),
            email=user_data.get('email'),
            password_hash=user_data.get('password_hash'),
            is_admin=user_data.get('is_admin', False)
        )
        db.session.add(user)
        db.session.commit()
        return user
    
    @staticmethod
    def update(user_id, update_data):
        from models import User
        db = get_db()
        user = db.session.get(User, int(user_id))
        if user:
            for key, value in update_data.items():
                setattr(user, key, value)
            db.session.commit()
    
    @staticmethod
    def find_all():
        from models import User
        return User.query.all()
    
    @staticmethod
    def count():
        from models import User
        return User.query.count()


class CategoryRepo:
    @staticmethod
    def find_by_id(category_id):
        from models import Category
        db = get_db()
        try:
            return db.session.get(Category, int(category_id))
        except (ValueError, TypeError):
            return None
    
    @staticmethod
    def find_by_name(name):
        from models import Category
        return Category.query.filter_by(name=name).first()
    
    @staticmethod
    def find_active():
        from models import Category
        return Category.query.filter_by(is_active=True).all()
    
    @staticmethod
    def find_all():
        from models import Category
        return Category.query.all()
    
    @staticmethod
    def create(category_data):
        from models import Category
        db = get_db()
        category = Category(
            name=category_data.get('name'),
            description=category_data.get('description', ''),
            image_url=category_data.get('image_url', ''),
            is_active=category_data.get('is_active', True)
        )
        db.session.add(category)
        db.session.commit()
        return category
    
    @staticmethod
    def update(category_id, update_data):
        from models import Category
        db = get_db()
        category = db.session.get(Category, int(category_id))
        if category:
            for key, value in update_data.items():
                setattr(category, key, value)
            db.session.commit()
    
    @staticmethod
    def delete(category_id):
        from models import Category
        db = get_db()
        category = db.session.get(Category, int(category_id))
        if category:
            db.session.delete(category)
            db.session.commit()
    
    @staticmethod
    def exists_by_name_exclude(name, exclude_id):
        from models import Category
        query = Category.query.filter(func.lower(Category.name) == func.lower(name))
        if exclude_id:
            query = query.filter(Category.id != int(exclude_id))
        return query.first() is not None
    
    @staticmethod
    def count():
        from models import Category
        return Category.query.count()


class ProductRepo:
    @staticmethod
    def find_by_id(product_id):
        from models import Product
        db = get_db()
        try:
            return db.session.get(Product, int(product_id))
        except (ValueError, TypeError):
            return None
    
    @staticmethod
    def find_all():
        from models import Product
        return Product.query.all()
    
    @staticmethod
    def find_by_category(category_name):
        from models import Product
        return Product.query.filter_by(category=category_name).all()
    
    @staticmethod
    def find_limit(limit):
        from models import Product
        return Product.query.limit(limit).all()
    
    @staticmethod
    def search(query_str, category=None):
        from models import Product
        query = Product.query
        
        if category and category != 'all':
            query = query.filter(Product.category.ilike(f'%{category}%'))
        
        if query_str:
            query = query.filter(
                or_(
                    Product.name.ilike(f'%{query_str}%'),
                    Product.description.ilike(f'%{query_str}%')
                )
            )
        
        return query.all()
    
    @staticmethod
    def create(product_data):
        from models import Product
        db = get_db()
        product = Product(
            name=product_data.get('name'),
            description=product_data.get('description'),
            price=product_data.get('price', 0),
            category=product_data.get('category'),
            category_id=product_data.get('category_id'),
            image_url=product_data.get('image_url'),
            stock=product_data.get('stock', 0)
        )
        db.session.add(product)
        db.session.commit()
        return product
    
    @staticmethod
    def update(product_id, update_data):
        from models import Product
        db = get_db()
        product = db.session.get(Product, int(product_id))
        if product:
            for key, value in update_data.items():
                setattr(product, key, value)
            db.session.commit()
    
    @staticmethod
    def delete(product_id):
        from models import Product
        db = get_db()
        product = db.session.get(Product, int(product_id))
        if product:
            db.session.delete(product)
            db.session.commit()
    
    @staticmethod
    def count():
        from models import Product
        return Product.query.count()


def _serialize_order_items(order):
    """Helper to serialize order items without mutating the relationship"""
    items_list = []
    for item in order.items.all():
        items_list.append({
            'product_id': str(item.product_id),
            'quantity': item.quantity,
            'price': item.price
        })
    order._serialized_items = items_list
    return order


class OrderWrapper:
    """Wrapper class to provide MongoDB-like access to order with serialized items"""
    def __init__(self, order, items_list):
        self._order = order
        self.items = items_list
        
    def __getattr__(self, name):
        return getattr(self._order, name)


class OrderRepo:
    @staticmethod
    def find_by_id(order_id):
        from models import Order
        db = get_db()
        try:
            order = db.session.get(Order, int(order_id))
            if order:
                items_list = [
                    {
                        'product_id': str(item.product_id),
                        'quantity': item.quantity,
                        'price': item.price
                    }
                    for item in order.items.all()
                ]
                return OrderWrapper(order, items_list)
            return None
        except (ValueError, TypeError):
            return None
    
    @staticmethod
    def find_by_user(user_id, sort_desc=True):
        from models import Order
        query = Order.query.filter_by(user_id=int(user_id))
        if sort_desc:
            query = query.order_by(Order.created_at.desc())
        else:
            query = query.order_by(Order.created_at.asc())
        orders = query.all()
        result = []
        for order in orders:
            items_list = [
                {
                    'product_id': str(item.product_id),
                    'quantity': item.quantity,
                    'price': item.price
                }
                for item in order.items.all()
            ]
            result.append(OrderWrapper(order, items_list))
        return result
    
    @staticmethod
    def find_all(sort_desc=True):
        from models import Order
        query = Order.query
        if sort_desc:
            query = query.order_by(Order.created_at.desc())
        else:
            query = query.order_by(Order.created_at.asc())
        orders = query.all()
        result = []
        for order in orders:
            items_list = [
                {
                    'product_id': str(item.product_id),
                    'quantity': item.quantity,
                    'price': item.price
                }
                for item in order.items.all()
            ]
            result.append(OrderWrapper(order, items_list))
        return result
    
    @staticmethod
    def find_recent(limit=10):
        from models import Order
        orders = Order.query.order_by(Order.created_at.desc()).limit(limit).all()
        result = []
        for order in orders:
            items_list = [
                {
                    'product_id': str(item.product_id),
                    'quantity': item.quantity,
                    'price': item.price
                }
                for item in order.items.all()
            ]
            result.append(OrderWrapper(order, items_list))
        return result
    
    @staticmethod
    def create(order_data):
        from models import Order, OrderItem
        db = get_db()
        order = Order(
            user_id=int(order_data.get('user_id')),
            total=order_data.get('total', 0),
            shipping_address=order_data.get('shipping_address'),
            status=order_data.get('status', 'pending'),
            payment_method=order_data.get('payment_method')
        )
        db.session.add(order)
        db.session.flush()
        
        items_data = order_data.get('items', [])
        for item_data in items_data:
            order_item = OrderItem(
                order_id=order.id,
                product_id=int(item_data.get('product_id')),
                quantity=item_data.get('quantity'),
                price=item_data.get('price')
            )
            db.session.add(order_item)
        
        db.session.commit()
        
        return OrderWrapper(order, items_data)
    
    @staticmethod
    def update(order_id, update_data):
        from models import Order
        db = get_db()
        order = db.session.get(Order, int(order_id))
        if order:
            for key, value in update_data.items():
                if key != 'items':
                    setattr(order, key, value)
            order.updated_at = datetime.utcnow()
            db.session.commit()
    
    @staticmethod
    def count():
        from models import Order
        return Order.query.count()
    
    @staticmethod
    def count_by_status(status):
        from models import Order
        return Order.query.filter_by(status=status).count()
    
    @staticmethod
    def sum_total():
        from models import Order
        result = Order.query.with_entities(func.sum(Order.total)).scalar()
        return result or 0


class ReviewRepo:
    @staticmethod
    def find_by_product(product_id):
        from models import Review
        return Review.query.filter_by(product_id=int(product_id)).all()
    
    @staticmethod
    def create(review_data):
        from models import Review
        db = get_db()
        review = Review(
            product_id=int(review_data.get('product_id')),
            user_id=int(review_data.get('user_id')),
            rating=review_data.get('rating'),
            comment=review_data.get('comment')
        )
        db.session.add(review)
        db.session.commit()
        return review
    
    @staticmethod
    def delete_by_product(product_id):
        from models import Review
        db = get_db()
        count = Review.query.filter_by(product_id=int(product_id)).delete()
        db.session.commit()
        return count
    
    @staticmethod
    def count():
        from models import Review
        return Review.query.count()


class AddressRepo:
    @staticmethod
    def find_by_id(address_id):
        from models import Address
        db = get_db()
        try:
            return db.session.get(Address, int(address_id))
        except (ValueError, TypeError):
            return None
    
    @staticmethod
    def find_by_user(user_id):
        from models import Address
        return Address.query.filter_by(user_id=int(user_id)).all()
    
    @staticmethod
    def create(address_data):
        from models import Address
        db = get_db()
        address = Address(
            user_id=int(address_data.get('user_id')),
            name=address_data.get('name'),
            street=address_data.get('street'),
            city=address_data.get('city'),
            state=address_data.get('state'),
            zip_code=address_data.get('zip_code'),
            phone=address_data.get('phone')
        )
        db.session.add(address)
        db.session.commit()
        return address
    
    @staticmethod
    def count():
        from models import Address
        return Address.query.count()


class VisitorLogRepo:
    @staticmethod
    def create(log_data):
        from models import VisitorLog
        db = get_db()
        log = VisitorLog(
            ip_address=log_data.get('ip_address'),
            user_agent=log_data.get('user_agent'),
            page=log_data.get('page')
        )
        db.session.add(log)
        db.session.commit()
    
    @staticmethod
    def count_daily():
        from models import VisitorLog
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        return VisitorLog.query.filter(
            VisitorLog.timestamp >= today
        ).with_entities(VisitorLog.ip_address).distinct().count()
    
    @staticmethod
    def get_weekly_data():
        from models import VisitorLog
        weekly_data = {}
        
        for i in range(7):
            date = datetime.utcnow() - timedelta(days=6-i)
            start = date.replace(hour=0, minute=0, second=0, microsecond=0)
            end = start + timedelta(days=1)
            
            count = VisitorLog.query.filter(
                VisitorLog.timestamp >= start,
                VisitorLog.timestamp < end
            ).with_entities(VisitorLog.ip_address).distinct().count()
            
            weekly_data[start.strftime('%Y-%m-%d')] = count
        
        return weekly_data


class OTPRepo:
    @staticmethod
    def find_by_email_purpose(email, purpose):
        from models import OTPCode
        return OTPCode.query.filter_by(email=email, purpose=purpose).first()
    
    @staticmethod
    def delete_by_email_purpose(email, purpose):
        from models import OTPCode
        db = get_db()
        OTPCode.query.filter_by(email=email, purpose=purpose).delete()
        db.session.commit()
    
    @staticmethod
    def create(otp_data):
        from models import OTPCode
        db = get_db()
        otp = OTPCode(
            email=otp_data.get('email'),
            purpose=otp_data.get('purpose'),
            otp=otp_data.get('otp'),
            attempts=otp_data.get('attempts', 0),
            expires_at=otp_data.get('expires_at')
        )
        db.session.add(otp)
        db.session.commit()
        return otp
    
    @staticmethod
    def update(otp_id, update_data):
        from models import OTPCode
        db = get_db()
        otp = db.session.get(OTPCode, int(otp_id))
        if otp:
            for key, value in update_data.items():
                setattr(otp, key, value)
            db.session.commit()
    
    @staticmethod
    def delete(otp_id):
        from models import OTPCode
        db = get_db()
        otp = db.session.get(OTPCode, int(otp_id))
        if otp:
            db.session.delete(otp)
            db.session.commit()


class TicketRepo:
    @staticmethod
    def find_by_id(ticket_id):
        from models import Ticket
        db = get_db()
        try:
            return db.session.get(Ticket, int(ticket_id))
        except (ValueError, TypeError):
            return None
    
    @staticmethod
    def find_by_user(user_id):
        from models import Ticket
        return Ticket.query.filter_by(user_id=int(user_id)).order_by(Ticket.created_at.desc()).all()
    
    @staticmethod
    def find_all(status=None, ticket_type=None):
        from models import Ticket
        query = Ticket.query
        if status:
            query = query.filter_by(status=status)
        if ticket_type:
            query = query.filter_by(ticket_type=ticket_type)
        return query.order_by(Ticket.created_at.desc()).all()
    
    @staticmethod
    def create(ticket_data):
        from models import Ticket
        db = get_db()
        ticket = Ticket(
            user_id=int(ticket_data.get('user_id')),
            order_id=int(ticket_data.get('order_id')) if ticket_data.get('order_id') else None,
            ticket_type=ticket_data.get('ticket_type'),
            subject=ticket_data.get('subject'),
            description=ticket_data.get('description'),
            status=ticket_data.get('status', 'open'),
            priority=ticket_data.get('priority', 'normal')
        )
        db.session.add(ticket)
        db.session.commit()
        return ticket
    
    @staticmethod
    def update(ticket_id, update_data):
        from models import Ticket
        db = get_db()
        ticket = db.session.get(Ticket, int(ticket_id))
        if ticket:
            for key, value in update_data.items():
                setattr(ticket, key, value)
            ticket.updated_at = datetime.utcnow()
            db.session.commit()
    
    @staticmethod
    def count():
        from models import Ticket
        return Ticket.query.count()
    
    @staticmethod
    def count_by_status(status):
        from models import Ticket
        return Ticket.query.filter_by(status=status).count()


class TicketMessageRepo:
    @staticmethod
    def find_by_ticket(ticket_id):
        from models import TicketMessage
        return TicketMessage.query.filter_by(ticket_id=int(ticket_id)).order_by(TicketMessage.created_at.asc()).all()
    
    @staticmethod
    def create(message_data):
        from models import TicketMessage
        db = get_db()
        message = TicketMessage(
            ticket_id=int(message_data.get('ticket_id')),
            author_id=int(message_data.get('author_id')),
            message=message_data.get('message'),
            is_admin_reply=message_data.get('is_admin_reply', False)
        )
        db.session.add(message)
        db.session.commit()
        return message
