from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
from models import User, Product, Order, Review, Address, VisitorLog, Category

# In-memory data storage
data_store = {
    'users': {},
    'products': {},
    'orders': {},
    'reviews': {},
    'addresses': {},
    'categories': {},
    'visitor_logs': [],
    'counters': {
        'user_id': 1,
        'product_id': 1,
        'order_id': 1,
        'review_id': 1,
        'address_id': 1,
        'category_id': 1
    }
}

def init_data_store():
    """Initialize the data store with sample data"""
    
    # Create admin user
    admin_user = User(
        user_id=1,
        username='admin',
        email='admin@nikitarasoi.com',
        password_hash=generate_password_hash('admin123'),
        is_admin=True
    )
    data_store['users'][1] = admin_user
    data_store['counters']['user_id'] = 2
    
    # Initialize categories
    categories_data = [
        {
            'name': 'Bread',
            'description': 'Fresh artisan breads, rolls, and baked goods made daily with premium ingredients.',
            'image_url': 'https://images.unsplash.com/photo-1549931319-a545dcf3bc73?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80'
        },
        {
            'name': 'Pastries',
            'description': 'Buttery, flaky pastries and croissants made with traditional French techniques.',
            'image_url': 'https://images.unsplash.com/photo-1578985545062-69928b1d9587?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80'
        },
        {
            'name': 'Muffins',
            'description': 'Moist and fluffy muffins with various flavors and mix-ins to start your day right.',
            'image_url': 'https://images.unsplash.com/photo-1587241321921-91a834d6d191?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80'
        },
        {
            'name': 'Desserts',
            'description': 'Decadent desserts, tarts, and sweet treats perfect for any special occasion.',
            'image_url': 'https://images.unsplash.com/photo-1551024506-0bccd828d307?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80'
        }
    ]
    
    for i, category_data in enumerate(categories_data, 1):
        category = Category(
            category_id=i,
            name=category_data['name'],
            description=category_data['description'],
            image_url=category_data['image_url']
        )
        data_store['categories'][i] = category
    
    data_store['counters']['category_id'] = len(categories_data) + 1
    
    # Sample products with stock photos
    products_data = [
        {
            'name': 'Artisan Sourdough Bread',
            'description': 'Traditional sourdough bread made with our signature starter, fermented for 24 hours for that perfect tangy flavor.',
            'price': 89.99,
            'category': 'Bread',
            'image_url': 'https://images.unsplash.com/photo-1549931319-a545dcf3bc73?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80',
            'stock': 15
        },
        {
            'name': 'Fresh Croissants',
            'description': 'Buttery, flaky croissants made fresh daily with premium French butter. Perfect for breakfast or afternoon tea.',
            'price': 129.99,
            'category': 'Pastries',
            'image_url': 'https://images.unsplash.com/photo-1578985545062-69928b1d9587?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80',
            'stock': 24
        },
        {
            'name': 'Chocolate Chip Muffins',
            'description': 'Moist and fluffy muffins loaded with premium chocolate chips. A family favorite!',
            'price': 159.99,
            'category': 'Muffins',
            'image_url': 'https://images.unsplash.com/photo-1587241321921-91a834d6d191?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80',
            'stock': 18
        },
        {
            'name': 'Danish Pastries',
            'description': 'Traditional Danish pastries with various fillings including cream cheese, fruit preserves, and custard.',
            'price': 189.99,
            'category': 'Pastries',
            'image_url': 'https://images.unsplash.com/photo-1517427294546-5aa121f68e8a?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80',
            'stock': 12
        },
        {
            'name': 'Whole Wheat Rolls',
            'description': 'Healthy whole wheat dinner rolls, perfect for any meal. Made with organic flour and seeds.',
            'price': 69.99,
            'category': 'Bread',
            'image_url': 'https://images.unsplash.com/photo-1508737804141-4c3b688e2546?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80',
            'stock': 20
        },
        {
            'name': 'Cinnamon Rolls',
            'description': 'Soft, gooey cinnamon rolls with cream cheese frosting. Baked fresh every morning.',
            'price': 149.99,
            'category': 'Pastries',
            'image_url': 'https://images.unsplash.com/photo-1509440159596-0249088772ff?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80',
            'stock': 16
        },
        {
            'name': 'Artisan Bagels',
            'description': 'Hand-rolled bagels available in various flavors: plain, sesame, poppy seed, and everything.',
            'price': 99.99,
            'category': 'Bread',
            'image_url': 'https://images.unsplash.com/photo-1506197603052-3cc9c3a201bd?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80',
            'stock': 22
        },
        {
            'name': 'Fruit Tarts',
            'description': 'Beautiful individual fruit tarts with pastry cream and fresh seasonal fruits.',
            'price': 229.99,
            'category': 'Desserts',
            'image_url': 'https://images.unsplash.com/photo-1551024506-0bccd828d307?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80',
            'stock': 8
        }
    ]
    
    for i, product_data in enumerate(products_data, 1):
        product = Product(
            product_id=i,
            name=product_data['name'],
            description=product_data['description'],
            price=product_data['price'],
            category=product_data['category'],
            image_url=product_data['image_url'],
            stock=product_data['stock']
        )
        data_store['products'][i] = product
    
    data_store['counters']['product_id'] = len(products_data) + 1

def get_next_id(counter_name):
    """Get next available ID for a given counter"""
    current_id = data_store['counters'][counter_name]
    data_store['counters'][counter_name] += 1
    return current_id

def add_visitor_log(ip_address, user_agent, page=None):
    """Add a visitor log entry"""
    visitor_log = VisitorLog(ip_address, user_agent, page)
    data_store['visitor_logs'].append(visitor_log)

def get_daily_visitors():
    """Get visitor count for today"""
    today = datetime.now().date()
    daily_visitors = [log for log in data_store['visitor_logs'] 
                     if log.timestamp.date() == today]
    return len(set(log.ip_address for log in daily_visitors))

def get_weekly_visitors():
    """Get visitor data for the past week"""
    week_ago = datetime.now() - timedelta(days=7)
    weekly_data = {}
    
    for i in range(7):
        date = (week_ago + timedelta(days=i)).date()
        daily_logs = [log for log in data_store['visitor_logs'] 
                     if log.timestamp.date() == date]
        weekly_data[date.strftime('%Y-%m-%d')] = len(set(log.ip_address for log in daily_logs))
    
    return weekly_data
