from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash

data_store = {'otp_codes': {}}


def init_data_store():
    """Initialize the database with sample data if empty"""
    from app import db
    from models import User, Category, Product

    if User.query.first() is not None:
        return

    admin_user = User(username='admin',
                      email='opgaming565710@gmail.com',
                      password_hash=generate_password_hash('admin123'),
                      is_admin=True)
    db.session.add(admin_user)

    categories_data = [{
        'name':
        'Bread',
        'description':
        'Fresh artisan breads, rolls, and baked goods made daily with premium ingredients.',
        'image_url':
        'https://images.unsplash.com/photo-1549931319-a545dcf3bc73?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80'
    }, {
        'name':
        'Pastries',
        'description':
        'Buttery, flaky pastries and croissants made with traditional French techniques.',
        'image_url':
        'https://images.unsplash.com/photo-1578985545062-69928b1d9587?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80'
    }, {
        'name':
        'Muffins',
        'description':
        'Moist and fluffy muffins with various flavors and mix-ins to start your day right.',
        'image_url':
        'https://images.unsplash.com/photo-1587241321921-91a834d6d191?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80'
    }, {
        'name':
        'Desserts',
        'description':
        'Decadent desserts, tarts, and sweet treats perfect for any special occasion.',
        'image_url':
        'https://images.unsplash.com/photo-1551024506-0bccd828d307?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80'
    }]

    for cat_data in categories_data:
        category = Category(name=cat_data['name'],
                            description=cat_data['description'],
                            image_url=cat_data['image_url'])
        db.session.add(category)

    db.session.commit()

    products_data = [{
        'name': 'Artisan Sourdough Bread',
        'description':
        'Traditional sourdough bread made with our signature starter, fermented for 24 hours for that perfect tangy flavor.',
        'price': 89.99,
        'category': 'Bread',
        'image_url':
        'https://images.unsplash.com/photo-1549931319-a545dcf3bc73?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80',
        'stock': 15
    }, {
        'name': 'Fresh Croissants',
        'description':
        'Buttery, flaky croissants made fresh daily with premium French butter. Perfect for breakfast or afternoon tea.',
        'price': 129.99,
        'category': 'Pastries',
        'image_url':
        'https://images.unsplash.com/photo-1578985545062-69928b1d9587?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80',
        'stock': 24
    }, {
        'name': 'Chocolate Chip Muffins',
        'description':
        'Moist and fluffy muffins loaded with premium chocolate chips. A family favorite!',
        'price': 159.99,
        'category': 'Muffins',
        'image_url':
        'https://images.unsplash.com/photo-1587241321921-91a834d6d191?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80',
        'stock': 18
    }, {
        'name': 'Danish Pastries',
        'description':
        'Traditional Danish pastries with various fillings including cream cheese, fruit preserves, and custard.',
        'price': 189.99,
        'category': 'Pastries',
        'image_url':
        'https://images.unsplash.com/photo-1517427294546-5aa121f68e8a?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80',
        'stock': 12
    }, {
        'name': 'Whole Wheat Rolls',
        'description':
        'Healthy whole wheat dinner rolls, perfect for any meal. Made with organic flour and seeds.',
        'price': 69.99,
        'category': 'Bread',
        'image_url':
        'https://images.unsplash.com/photo-1508737804141-4c3b688e2546?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80',
        'stock': 20
    }, {
        'name': 'Cinnamon Rolls',
        'description':
        'Soft, gooey cinnamon rolls with cream cheese frosting. Baked fresh every morning.',
        'price': 149.99,
        'category': 'Pastries',
        'image_url':
        'https://images.unsplash.com/photo-1509440159596-0249088772ff?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80',
        'stock': 16
    }, {
        'name': 'Artisan Bagels',
        'description':
        'Hand-rolled bagels available in various flavors: plain, sesame, poppy seed, and everything.',
        'price': 99.99,
        'category': 'Bread',
        'image_url':
        'https://images.unsplash.com/photo-1506197603052-3cc9c3a201bd?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80',
        'stock': 22
    }, {
        'name': 'Fruit Tarts',
        'description':
        'Beautiful individual fruit tarts with pastry cream and fresh seasonal fruits.',
        'price': 229.99,
        'category': 'Desserts',
        'image_url':
        'https://images.unsplash.com/photo-1551024506-0bccd828d307?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80',
        'stock': 8
    }]

    for product_data in products_data:
        cat = Category.query.filter_by(name=product_data['category']).first()
        product = Product(name=product_data['name'],
                          description=product_data['description'],
                          price=product_data['price'],
                          category=product_data['category'],
                          category_id=cat.id if cat else None,
                          image_url=product_data['image_url'],
                          stock=product_data['stock'])
        db.session.add(product)

    db.session.commit()


def add_visitor_log(ip_address, user_agent, page=None):
    """Add a visitor log entry"""
    from app import db
    from models import VisitorLog

    visitor_log = VisitorLog(ip_address=ip_address,
                             user_agent=user_agent,
                             page=page)
    db.session.add(visitor_log)
    try:
        db.session.commit()
    except:
        db.session.rollback()


def get_daily_visitors():
    """Get visitor count for today"""
    from models import VisitorLog
    from sqlalchemy import func

    today = datetime.now().date()
    count = VisitorLog.query.filter(
        func.date(VisitorLog.timestamp) == today).distinct(
            VisitorLog.ip_address).count()
    return count


def get_weekly_visitors():
    """Get visitor data for the past week"""
    from models import VisitorLog
    from sqlalchemy import func

    week_ago = datetime.now() - timedelta(days=7)
    weekly_data = {}

    for i in range(7):
        date = (week_ago + timedelta(days=i)).date()
        count = VisitorLog.query.filter(
            func.date(VisitorLog.timestamp) == date).distinct(
                VisitorLog.ip_address).count()
        weekly_data[date.strftime('%Y-%m-%d')] = count

    return weekly_data
