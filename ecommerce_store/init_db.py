"""
Database initialization script with sample data
Demonstrates usage of Factory, Facade, and Strategy patterns
"""
from app import app
from models.db import db_manager, db
from models.user import User
from models.product import Category, Brand, Product, ProductSpecification
from factories.user_factory import create_user
from services.facade import AuthServiceFacade

def init_database():
    """Initialize database with sample data"""
    
    with app.app_context():
        # Drop all tables and recreate (WARNING: This will delete all data!)
        print("Dropping existing tables...")
        db.drop_all()
        
        print("Creating new tables...")
        db.create_all()
        
        # Create admin user using Factory pattern
        print("\nCreating admin user (Factory Pattern)...")
        admin = create_user(
            email='admin@ezgadgets.com',
            username='admin',
            password='admin123',
            user_type='admin',
            first_name='Admin',
            last_name='User'
        )
        db.session.add(admin)
        
        # Create sample customer using Facade pattern
        print("Creating sample customer (Facade Pattern)...")
        success, message, customer = AuthServiceFacade.register_user(
            email='customer@example.com',
            username='customer',
            password='customer123',
            user_type='customer',
            first_name='John',
            last_name='Doe',
            phone='01819-940370'
        )
        print(f"  {message}")
        
        # Create categories
        print("\nCreating categories...")
        categories_data = [
            ('Mousepad', 'mousepad'),
            ('Mouse', 'mouse'),
            ('Monitor', 'monitors'),
            ('Microphone', 'microphone'),
            ('Keyboard', 'keyboard'),
            ('Headset', 'headset'),
            ('Gamepad', 'gamepad'),
            ('3d Printing', '3d-printing'),
            ('Pc Components', 'pc-components'),
            ('Peripherals', 'peripherals'),
            ('E-Reader', 'e-reader'),
            ('Accessories', 'accessories'),
        ]
        
        categories = {}
        for name, slug in categories_data:
            cat = Category(name=name, slug=slug)
            db.session.add(cat)
            categories[slug] = cat
            print(f"  Created category: {name}")
        
        # Create brands
        print("\nCreating brands...")
        brands_data = [
            ('8BitDo', '8bitdo'),
            ('Bigbigwon', 'bigbigwon'),
            ('EasySMX', 'easysmx'),
            ('Flydigi', 'flydigi'),
            ('GameSir', 'gamesir'),
            ('Manba', 'manba'),
            ('Aula', 'aula'),
            ('Eweadn', 'eweadn'),
            ('ATK', 'atk'),
            ('Marvo', 'marvo'),
            ('Lingbao', 'lingbao'),
            ('HyperX', 'hyperx'),
            ('Samsung', 'samsung'),
        ]
        
        brands = {}
        for name, slug in brands_data:
            brand = Brand(name=name, slug=slug)
            db.session.add(brand)
            brands[slug] = brand
            print(f"  Created brand: {name}")
        
        db.session.commit()
        
        # Create sample products
        print("\nCreating sample products...")
        
        products_data = [
            {
                'name': '8BitDo Ultimate 2C Wireless Controller',
                'slug': '8bitdo-ultimate-2c-wireless-controller',
                'price': 2799.00,
                'original_price': 2999.00,
                'stock': 15,
                'category': 'gamepad',
                'brand': '8bitdo',
                'is_featured': True,
                'is_new': True,
                'is_hot': True,
                'description': 'Take full control of your gaming experience with the 8BitDo Ultimate 2C Wireless Controller.',
                'short_description': 'Switch / PC / Android / iOS compatible\nBluetooth / 2.4G / Wired connection\nErgonomic design for comfort',
                'warranty_period': '1 Year',
            },
            {
                'name': 'Bigbigwon Aether Tri-mode Wireless Hall-effect Controller',
                'slug': 'bigbigwon-aether-tri-mode-wireless-controller',
                'price': 2550.00,
                'stock': 0,
                'category': 'gamepad',
                'brand': 'bigbigwon',
                'is_featured': True,
                'is_hot': True,
                'description': 'Professional gaming controller with hall-effect sensors.',
                'warranty_period': '1 Year',
            },
            {
                'name': 'AULA F75 Wireless Tri-Mode Mechanical Keyboard',
                'slug': 'aula-f75-wireless-tri-mode-mechanical-keyboard',
                'price': 5250.00,
                'original_price': 5450.00,
                'stock': 25,
                'category': 'keyboard',
                'brand': 'aula',
                'is_featured': True,
                'is_new': True,
                'discount_percentage': 4,
                'description': 'Premium mechanical keyboard with RGB backlighting.',
                'warranty_period': '1 Year',
            },
            {
                'name': 'LINGBAO M1 Pro 1000Hz Wireless Gaming Mouse',
                'slug': 'lingbao-m1-pro-1000hz-wireless-gaming-mouse',
                'price': 2099.00,
                'stock': 30,
                'category': 'mouse',
                'brand': 'lingbao',
                'is_featured': True,
                'description': 'High-precision wireless gaming mouse with 1000Hz polling rate.',
                'warranty_period': '1 Year',
            },
            {
                'name': 'MARVO Niro 40 G950 Gaming Mouse',
                'slug': 'marvo-niro-40-g950-gaming-mouse',
                'price': 1599.00,
                'stock': 20,
                'category': 'mouse',
                'brand': 'marvo',
                'is_featured': True,
                'is_new': True,
                'description': 'Ergonomic gaming mouse with customizable RGB lighting.',
                'warranty_period': '1 Year',
            },
            {
                'name': 'EWEADN S9+ Ultra Gaming Mouse',
                'slug': 'eweadn-s9-plus-ultra-gaming-mouse',
                'price': 3299.00,
                'stock': 12,
                'category': 'mouse',
                'brand': 'eweadn',
                'is_featured': True,
                'description': 'Ultra-lightweight wireless gaming mouse.',
                'warranty_period': '1 Year',
            },
            {
                'name': 'ATK Blazing Sky X1 Wireless Gaming Mouse',
                'slug': 'atk-blazing-sky-x1-wireless-gaming-mouse',
                'price': 4199.00,
                'stock': 0,
                'category': 'mouse',
                'brand': 'atk',
                'is_hot': True,
                'description': 'Professional wireless gaming mouse.',
                'warranty_period': '1 Year',
            },
            {
                'name': 'ATK Blazing Sky F1 Ultimate Gaming Mouse',
                'slug': 'atk-blazing-sky-f1-ultimate-gaming-mouse',
                'price': 3899.00,
                'stock': 18,
                'category': 'mouse',
                'brand': 'atk',
                'is_featured': True,
                'description': 'Ultimate precision gaming mouse.',
                'warranty_period': '1 Year',
            },
            {
                'name': 'EWEADN GS01 Pro Wireless Gaming Mouse',
                'slug': 'eweadn-gs01-pro-wireless-gaming-mouse',
                'price': 2799.00,
                'original_price': 3199.00,
                'stock': 22,
                'category': 'mouse',
                'brand': 'eweadn',
                'is_featured': True,
                'discount_percentage': 13,
                'description': 'Professional wireless gaming mouse with ergonomic design.',
                'warranty_period': '1 Year',
            },
            {
                'name': 'ATK Blazing Sky Duckbill Wireless Mouse',
                'slug': 'atk-blazing-sky-duckbill-wireless-mouse',
                'price': 3599.00,
                'original_price': 3999.00,
                'stock': 15,
                'category': 'mouse',
                'brand': 'atk',
                'is_featured': True,
                'discount_percentage': 10,
                'description': 'Unique duckbill design wireless mouse.',
                'warranty_period': '1 Year',
            },
            {
                'name': 'AULA F75 RGB Backlit Wired Hot Swappable Keyboard',
                'slug': 'aula-f75-rgb-backlit-wired-keyboard',
                'price': 2499.00,
                'original_price': 3199.00,
                'stock': 20,
                'category': 'keyboard',
                'brand': 'aula',
                'is_featured': True,
                'description': 'Hot-swappable mechanical keyboard with RGB.',
                'warranty_period': '1 Year',
            },
            {
                'name': 'AULA F75 MAX Tri-Mode Wireless Gasket Keyboard',
                'slug': 'aula-f75-max-tri-mode-wireless-gasket-keyboard',
                'price': 5950.00,
                'original_price': 5999.00,
                'stock': 8,
                'category': 'keyboard',
                'brand': 'aula',
                'is_featured': True,
                'description': 'Premium gasket-mounted keyboard.',
                'warranty_period': '1 Year',
            },
            {
                'name': 'AULA SC390 Tri-Mode Lightweight Gaming Mouse',
                'slug': 'aula-sc390-tri-mode-lightweight-gaming-mouse',
                'price': 2299.00,
                'stock': 25,
                'category': 'mouse',
                'brand': 'aula',
                'is_featured': True,
                'description': 'Ultra-lightweight tri-mode gaming mouse.',
                'warranty_period': '1 Year',
            },
            {
                'name': 'AULA AU75 Tri-Mode Mechanical Keyboard',
                'slug': 'aula-au75-tri-mode-mechanical-keyboard',
                'price': 4500.00,
                'original_price': 4800.00,
                'stock': 12,
                'category': 'keyboard',
                'brand': 'aula',
                'is_featured': True,
                'description': 'Versatile tri-mode mechanical keyboard.',
                'warranty_period': '1 Year',
            },
            {
                'name': 'HyperX QuadCast S - Black USB Condenser Microphone',
                'slug': 'hyperx-quadcast-s-black-usb-condenser-microphone',
                'price': 16000.00,
                'stock': 5,
                'category': 'microphone',
                'brand': 'hyperx',
                'is_featured': True,
                'description': 'Professional USB condenser microphone with RGB.',
                'warranty_period': '2 Years',
            },
            {
                'name': 'HyperX SoloCast - Black USB Gaming Microphone',
                'slug': 'hyperx-solocast-black-usb-gaming-microphone',
                'price': 7500.00,
                'stock': 10,
                'category': 'microphone',
                'brand': 'hyperx',
                'is_featured': True,
                'description': 'Compact USB gaming microphone.',
                'warranty_period': '2 Years',
            },
            {
                'name': 'Samsung Odyssey G5 G50SF QHD 180Hz 27" Gaming Monitor',
                'slug': 'samsung-odyssey-g5-g50sf-qhd-180hz-27-gaming-monitor',
                'price': 75000.00,
                'stock': 3,
                'category': 'monitors',
                'brand': 'samsung',
                'is_featured': True,
                'description': 'High-performance QHD gaming monitor.',
                'warranty_period': '3 Years',
            },
            {
                'name': 'GameSir Cyclone 2 Multiplatform Controller',
                'slug': 'gamesir-cyclone-2-multiplatform-controller',
                'price': 4999.00,
                'original_price': 5799.00,
                'stock': 18,
                'category': 'gamepad',
                'brand': 'gamesir',
                'is_featured': True,
                'is_hot': True,
                'description': 'Universal gaming controller for all platforms.',
                'short_description': 'Switch / PC / Android / iOS compatible\nBluetooth / 2.4G / Wired connection\nRGB lighting and vibration',
                'warranty_period': '1 Year',
            },
        ]
        
        for prod_data in products_data:
            category = categories.get(prod_data.pop('category'))
            brand = brands.get(prod_data.pop('brand'))
            
            product = Product(
                category_id=category.id if category else None,
                brand_id=brand.id if brand else None,
                main_image=f"https://via.placeholder.com/500?text={prod_data['name'][:20]}",
                **prod_data
            )
            db.session.add(product)
            print(f"  Created product: {product.name}")
        
        db.session.commit()
        print(f"\nDatabase initialized successfully!")
        print(f"\nLogin credentials:")
        print(f"  Admin - Email: admin@ezgadgets.com, Password: admin123")
        print(f"  Customer - Email: customer@example.com, Password: customer123")


if __name__ == '__main__':
    init_database()
