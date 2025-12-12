#!/usr/bin/env python3
"""
Initialize the database with sample data for CaupenRost
Supports both SQLAlchemy (SQLite/PostgreSQL) and MongoDB backends.

Usage:
    python init_data.py              # Initialize/seed database
    python init_data.py --reset      # Drop all data and reinitialize
    python init_data.py --mongo      # Force MongoDB mode (requires MONGO_URI env var)
"""

import os
import sys
import logging
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

USE_MONGODB = bool(os.environ.get('MONGO_URI')) or '--mongo' in sys.argv
RESET_DB = '--reset' in sys.argv


def init_mongodb():
    """Initialize MongoDB with sample data"""
    from mongo_db import (MongoUserRepo, MongoCategoryRepo, MongoProductRepo,
                         MongoOrderRepo, MongoReviewRepo, MongoAddressRepo,
                         MongoVisitorLogRepo, get_mongo_db)
    
    db = get_mongo_db()
    
    if RESET_DB:
        logger.info("Resetting MongoDB collections...")
        db['users'].delete_many({})
        db['categories'].delete_many({})
        db['products'].delete_many({})
        db['orders'].delete_many({})
        db['reviews'].delete_many({})
        db['addresses'].delete_many({})
        db['visitor_logs'].delete_many({})
        db['otp_codes'].delete_many({})
    
    if MongoUserRepo.count() == 0:
        logger.info("Creating admin user...")
        MongoUserRepo.create({
            'username': 'admin',
            'email': 'opgaming565710@gmail.com',
            'password_hash': generate_password_hash('admin123'),
            'is_admin': True
        })
        
        logger.info("Creating sample users...")
        users = [
            {'username': 'john_doe', 'email': 'john@example.com', 'password_hash': generate_password_hash('Password1!')},
            {'username': 'sarah_baker', 'email': 'sarah@example.com', 'password_hash': generate_password_hash('Password1!')},
        ]
        for user_data in users:
            MongoUserRepo.create(user_data)
    
    if MongoCategoryRepo.count() == 0:
        logger.info("Creating categories...")
        categories = [
            {'name': 'Bread', 'description': 'Fresh artisan breads, rolls, and baked goods made daily with premium ingredients.', 'image_url': 'https://images.unsplash.com/photo-1549931319-a545dcf3bc73?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80'},
            {'name': 'Pastries', 'description': 'Buttery, flaky pastries and croissants made with traditional French techniques.', 'image_url': 'https://images.unsplash.com/photo-1578985545062-69928b1d9587?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80'},
            {'name': 'Muffins', 'description': 'Moist and fluffy muffins with various flavors and mix-ins to start your day right.', 'image_url': 'https://images.unsplash.com/photo-1587241321921-91a834d6d191?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80'},
            {'name': 'Desserts', 'description': 'Decadent desserts, tarts, and sweet treats perfect for any special occasion.', 'image_url': 'https://images.unsplash.com/photo-1551024506-0bccd828d307?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80'},
        ]
        for cat_data in categories:
            MongoCategoryRepo.create(cat_data)
    
    if MongoProductRepo.count() == 0:
        logger.info("Creating products...")
        products = [
            {'name': 'Artisan Sourdough Bread', 'description': 'Traditional sourdough bread made with our signature starter.', 'price': 89.99, 'category': 'Bread', 'image_url': 'https://images.unsplash.com/photo-1549931319-a545dcf3bc73', 'stock': 15},
            {'name': 'Fresh Croissants', 'description': 'Buttery, flaky croissants made fresh daily with premium French butter.', 'price': 129.99, 'category': 'Pastries', 'image_url': 'https://images.unsplash.com/photo-1578985545062-69928b1d9587', 'stock': 24},
            {'name': 'Chocolate Chip Muffins', 'description': 'Moist and fluffy muffins loaded with premium chocolate chips.', 'price': 159.99, 'category': 'Muffins', 'image_url': 'https://images.unsplash.com/photo-1587241321921-91a834d6d191', 'stock': 18},
            {'name': 'Fruit Tarts', 'description': 'Beautiful individual fruit tarts with pastry cream and fresh seasonal fruits.', 'price': 229.99, 'category': 'Desserts', 'image_url': 'https://images.unsplash.com/photo-1551024506-0bccd828d307', 'stock': 8},
            {'name': 'Cinnamon Rolls', 'description': 'Soft, gooey cinnamon rolls with cream cheese frosting.', 'price': 149.99, 'category': 'Pastries', 'image_url': 'https://images.unsplash.com/photo-1509440159596-0249088772ff', 'stock': 16},
            {'name': 'Whole Wheat Rolls', 'description': 'Healthy whole wheat dinner rolls, perfect for any meal.', 'price': 69.99, 'category': 'Bread', 'image_url': 'https://images.unsplash.com/photo-1508737804141-4c3b688e2546', 'stock': 20},
        ]
        for product_data in products:
            cat = MongoCategoryRepo.find_by_name(product_data['category'])
            if cat:
                product_data['category_id'] = str(cat.id)
            MongoProductRepo.create(product_data)
    else:
        logger.info("Backfilling missing category_id for existing products...")
        all_products = MongoProductRepo.find_all()
        for product in all_products:
            if not product.category_id and product.category:
                cat = MongoCategoryRepo.find_by_name(product.category)
                if cat:
                    MongoProductRepo.update(product.id, {'category_id': str(cat.id)})
    
    logger.info("MongoDB initialization complete!")
    logger.info("Admin login: admin / admin123")
    logger.info("Sample user login: john_doe / Password1!")


def init_sqlalchemy():
    """Initialize SQLAlchemy database with sample data"""
    from app import app, db
    from models import User, Category, Product, Order, OrderItem, Review, Address, VisitorLog
    
    with app.app_context():
        if RESET_DB:
            logger.info("Resetting SQLAlchemy database...")
            db.drop_all()
            db.create_all()
        else:
            db.create_all()
        
        if User.query.count() == 0:
            logger.info("Creating admin user...")
            admin_user = User(
                username='admin',
                email='opgaming565710@gmail.com',
                password_hash=generate_password_hash('admin123'),
                is_admin=True
            )
            db.session.add(admin_user)
            
            logger.info("Creating sample users...")
            users = [
                User(username='john_doe', email='john@example.com', password_hash=generate_password_hash('Password1!')),
                User(username='sarah_baker', email='sarah@example.com', password_hash=generate_password_hash('Password1!')),
            ]
            for user in users:
                db.session.add(user)
            db.session.commit()
        
        if Category.query.count() == 0:
            logger.info("Creating categories...")
            categories = [
                Category(name='Bread', description='Fresh artisan breads, rolls, and baked goods made daily with premium ingredients.', image_url='https://images.unsplash.com/photo-1549931319-a545dcf3bc73?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80'),
                Category(name='Pastries', description='Buttery, flaky pastries and croissants made with traditional French techniques.', image_url='https://images.unsplash.com/photo-1578985545062-69928b1d9587?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80'),
                Category(name='Muffins', description='Moist and fluffy muffins with various flavors and mix-ins to start your day right.', image_url='https://images.unsplash.com/photo-1587241321921-91a834d6d191?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80'),
                Category(name='Desserts', description='Decadent desserts, tarts, and sweet treats perfect for any special occasion.', image_url='https://images.unsplash.com/photo-1551024506-0bccd828d307?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80'),
            ]
            for cat in categories:
                db.session.add(cat)
            db.session.commit()
        
        if Product.query.count() == 0:
            logger.info("Creating products...")
            bread_cat = Category.query.filter_by(name='Bread').first()
            pastries_cat = Category.query.filter_by(name='Pastries').first()
            muffins_cat = Category.query.filter_by(name='Muffins').first()
            desserts_cat = Category.query.filter_by(name='Desserts').first()
            
            products = [
                Product(name='Artisan Sourdough Bread', description='Traditional sourdough bread made with our signature starter.', price=89.99, category='Bread', category_id=bread_cat.id if bread_cat else None, image_url='https://images.unsplash.com/photo-1549931319-a545dcf3bc73', stock=15),
                Product(name='Fresh Croissants', description='Buttery, flaky croissants made fresh daily with premium French butter.', price=129.99, category='Pastries', category_id=pastries_cat.id if pastries_cat else None, image_url='https://images.unsplash.com/photo-1578985545062-69928b1d9587', stock=24),
                Product(name='Chocolate Chip Muffins', description='Moist and fluffy muffins loaded with premium chocolate chips.', price=159.99, category='Muffins', category_id=muffins_cat.id if muffins_cat else None, image_url='https://images.unsplash.com/photo-1587241321921-91a834d6d191', stock=18),
                Product(name='Fruit Tarts', description='Beautiful individual fruit tarts with pastry cream and fresh seasonal fruits.', price=229.99, category='Desserts', category_id=desserts_cat.id if desserts_cat else None, image_url='https://images.unsplash.com/photo-1551024506-0bccd828d307', stock=8),
                Product(name='Cinnamon Rolls', description='Soft, gooey cinnamon rolls with cream cheese frosting.', price=149.99, category='Pastries', category_id=pastries_cat.id if pastries_cat else None, image_url='https://images.unsplash.com/photo-1509440159596-0249088772ff', stock=16),
                Product(name='Whole Wheat Rolls', description='Healthy whole wheat dinner rolls, perfect for any meal.', price=69.99, category='Bread', category_id=bread_cat.id if bread_cat else None, image_url='https://images.unsplash.com/photo-1508737804141-4c3b688e2546', stock=20),
            ]
            for product in products:
                db.session.add(product)
            db.session.commit()
        
        logger.info("SQLAlchemy database initialization complete!")
        logger.info("Admin login: admin / admin123")
        logger.info("Sample user login: john_doe / Password1!")


def main():
    """Main entry point"""
    print("=" * 50)
    print("CaupenRost Database Initialization")
    print("=" * 50)
    
    if USE_MONGODB:
        if not os.environ.get('MONGO_URI'):
            logger.error("MONGO_URI environment variable is required for MongoDB mode")
            logger.info("Set MONGO_URI=mongodb://localhost:27017/caupenrost")
            sys.exit(1)
        logger.info("Using MongoDB backend")
        init_mongodb()
    else:
        logger.info("Using SQLAlchemy backend (SQLite/PostgreSQL)")
        init_sqlalchemy()
    
    print("=" * 50)
    print("Initialization complete!")
    print("=" * 50)


if __name__ == '__main__':
    main()
