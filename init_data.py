#!/usr/bin/env python3
"""
Initialize the database with sample data for NIKITA RASOI & BAKES
"""

from app import app, db
from models import User, Product, Order, Review, Address, OrderItem, VisitorLog
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)

def init_database():
    """Initialize database with sample data"""
    with app.app_context():
        # Drop all tables and recreate them
        db.drop_all()
        db.create_all()
        
        # Create admin user
        admin_user = User(
            username='admin',
            email='opgaming565710@gmail.com',
            password_hash=generate_password_hash('admin123'),
            is_admin=True
        )
        db.session.add(admin_user)
        
        # Create some regular users
        users = [
            User(username='john_doe', email='john@example.com', password_hash=generate_password_hash('password123')),
            User(username='sarah_baker', email='sarah@example.com', password_hash=generate_password_hash('password123')),
            User(username='mike_sweet', email='mike@example.com', password_hash=generate_password_hash('password123'))
        ]
        
        for user in users:
            db.session.add(user)
        
        # Create sample products (in INR)
        products = [
            Product(
                name='Chocolate Truffle Cake',
                description='Rich and decadent chocolate cake with chocolate ganache',
                price=850.00,
                category='Cakes',
                image_url='https://cdn.pixabay.com/photo/2016/11/22/18/54/cake-1851142_1280.jpg',
                stock=15
            ),
            Product(
                name='Vanilla Bean Cupcakes',
                description='Classic vanilla cupcakes with buttercream frosting',
                price=120.00,
                category='Cupcakes',
                image_url='https://cdn.pixabay.com/photo/2018/04/11/16/39/cupcake-3309789_1280.jpg',
                stock=24
            ),
            Product(
                name='Fresh Strawberry Tart',
                description='Buttery pastry shell filled with pastry cream and fresh strawberries',
                price=450.00,
                category='Tarts',
                image_url='https://cdn.pixabay.com/photo/2017/05/01/05/18/pastry-2274750_1280.jpg',
                stock=8
            ),
            Product(
                name='Artisan Sourdough Bread',
                description='Freshly baked sourdough with a perfect crust',
                price=180.00,
                category='Bread',
                image_url='https://cdn.pixabay.com/photo/2017/06/23/23/58/bread-2434370_1280.jpg',
                stock=12
            ),
            Product(
                name='Red Velvet Cake',
                description='Classic red velvet cake with cream cheese frosting',
                price=920.00,
                category='Cakes',
                image_url='https://cdn.pixabay.com/photo/2018/02/21/03/19/cake-3169966_1280.jpg',
                stock=10
            ),
            Product(
                name='Chocolate Chip Cookies',
                description='Homemade chocolate chip cookies - pack of 12',
                price=280.00,
                category='Cookies',
                image_url='https://cdn.pixabay.com/photo/2014/07/08/12/34/cookies-386761_1280.jpg',
                stock=30
            ),
            Product(
                name='Lemon Meringue Pie',
                description='Tangy lemon curd topped with fluffy meringue',
                price=650.00,
                category='Pies',
                image_url='https://cdn.pixabay.com/photo/2017/01/11/11/33/cake-1971552_1280.jpg',
                stock=6
            ),
            Product(
                name='Cinnamon Rolls',
                description='Warm cinnamon rolls with glaze - pack of 6',
                price=320.00,
                category='Pastries',
                image_url='https://cdn.pixabay.com/photo/2016/03/27/22/16/cinnamon-roll-1284543_1280.jpg',
                stock=18
            ),
            Product(
                name='Black Forest Cake',
                description='Chocolate sponge with cherries and whipped cream',
                price=1050.00,
                category='Cakes',
                image_url='https://cdn.pixabay.com/photo/2017/01/11/11/33/cake-1971555_1280.jpg',
                stock=8
            ),
            Product(
                name='Apple Pie',
                description='Traditional apple pie with lattice crust',
                price=580.00,
                category='Pies',
                image_url='https://cdn.pixabay.com/photo/2016/03/05/20/02/apple-pie-1238510_1280.jpg',
                stock=12
            ),
            Product(
                name='Blueberry Muffins',
                description='Fresh blueberry muffins - pack of 6',
                price=240.00,
                category='Muffins',
                image_url='https://cdn.pixabay.com/photo/2014/07/08/12/35/muffin-386646_1280.jpg',
                stock=20
            ),
            Product(
                name='Cheesecake',
                description='New York style cheesecake with berry compote',
                price=750.00,
                category='Cakes',
                image_url='https://cdn.pixabay.com/photo/2017/05/12/08/29/cheesecake-2306966_1280.jpg',
                stock=9
            )
        ]
        
        for product in products:
            db.session.add(product)
        
        # Commit users and products first
        db.session.commit()
        
        # Create sample addresses
        addresses = [
            Address(
                user_id=users[0].id,
                name='John Doe',
                street='123 Main Street',
                city='Mumbai',
                state='Maharashtra',
                zip_code='400001'
            ),
            Address(
                user_id=users[1].id,
                name='Sarah Baker',
                street='456 Oak Avenue',
                city='Delhi',
                state='Delhi',
                zip_code='110001'
            )
        ]
        
        for address in addresses:
            db.session.add(address)
        
        # Create sample orders
        sample_order = Order(
            user_id=users[0].id,
            total=1170.00,
            status='delivered',
            created_at=datetime.utcnow() - timedelta(days=2)
        )
        db.session.add(sample_order)
        db.session.commit()
        
        # Create order items
        order_items = [
            OrderItem(
                order_id=sample_order.id,
                product_id=products[0].id,  # Chocolate Truffle Cake
                quantity=1,
                price=products[0].price
            ),
            OrderItem(
                order_id=sample_order.id,
                product_id=products[5].id,  # Chocolate Chip Cookies
                quantity=1,
                price=products[5].price
            )
        ]
        
        for item in order_items:
            db.session.add(item)
        
        # Create sample reviews
        reviews = [
            Review(
                product_id=products[0].id,
                user_id=users[0].id,
                rating=5,
                comment='Amazing chocolate cake! Rich and delicious.',
                created_at=datetime.utcnow() - timedelta(days=1)
            ),
            Review(
                product_id=products[1].id,
                user_id=users[1].id,
                rating=4,
                comment='Lovely vanilla cupcakes, kids loved them!',
                created_at=datetime.utcnow() - timedelta(hours=12)
            ),
            Review(
                product_id=products[0].id,
                user_id=users[2].id,
                rating=5,
                comment='Best chocolate cake in the city!',
                created_at=datetime.utcnow() - timedelta(hours=6)
            )
        ]
        
        for review in reviews:
            db.session.add(review)
        
        # Create sample visitor logs
        for i in range(50):
            visitor_log = VisitorLog(
                ip_address=f'192.168.1.{i + 100}',
                user_agent='Mozilla/5.0 (compatible sample)',
                timestamp=datetime.utcnow() - timedelta(hours=i)
            )
            db.session.add(visitor_log)
        
        # Commit all changes
        db.session.commit()
        
        logging.info("Database initialized successfully!")
        logging.info(f"Created {len(users) + 1} users (including admin)")
        logging.info(f"Created {len(products)} products")
        logging.info(f"Created {len(addresses)} addresses")
        logging.info(f"Created 1 sample order with {len(order_items)} items")
        logging.info(f"Created {len(reviews)} reviews")
        logging.info("Created 50 visitor log entries")
        
        print("Database initialization complete!")
        print("Admin login: admin / admin123")
        print("Sample user login: john_doe / password123")

if __name__ == '__main__':
    init_database()