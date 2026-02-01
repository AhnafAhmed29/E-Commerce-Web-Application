import sqlite3
from contextlib import contextmanager
import os
from datetime import datetime
import hashlib

DATABASE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database', 'store.db')

@contextmanager
def get_db_connection():
    """Context manager for database connections"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def hash_password(password):
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def init_database():
    """Initialize database with all tables and sample data"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                name TEXT NOT NULL,
                phone TEXT,
                address TEXT,
                role TEXT DEFAULT 'customer',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create products table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                price REAL NOT NULL,
                stock INTEGER NOT NULL DEFAULT 0,
                image TEXT,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create product_specs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS product_specs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER NOT NULL,
                spec TEXT NOT NULL,
                FOREIGN KEY (product_id) REFERENCES products (id) ON DELETE CASCADE
            )
        ''')
        
        # Create orders table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                customer_name TEXT NOT NULL,
                customer_email TEXT NOT NULL,
                customer_phone TEXT NOT NULL,
                customer_address TEXT NOT NULL,
                total_amount REAL NOT NULL,
                payment_method TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Create order_items table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS order_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                product_name TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                price REAL NOT NULL,
                FOREIGN KEY (order_id) REFERENCES orders (id) ON DELETE CASCADE,
                FOREIGN KEY (product_id) REFERENCES products (id)
            )
        ''')
        
        # Create default admin user if not exists
        cursor.execute('SELECT COUNT(*) FROM users WHERE role = "admin"')
        if cursor.fetchone()[0] == 0:
            admin_password = hash_password('admin123')
            cursor.execute('''
                INSERT INTO users (email, password, name, phone, role)
                VALUES (?, ?, ?, ?, ?)
            ''', ('admin@ezgadgets.com', admin_password, 'Admin User', '01819940370', 'admin'))
        
        # Check if products exist
        cursor.execute('SELECT COUNT(*) FROM products')
        if cursor.fetchone()[0] == 0:
            # Insert sample products
            sample_products = [
                ('RGB Gaming Keyboard', 'Keyboards', 89.99, 25, 'keyboard.jpg', 'Mechanical RGB keyboard with customizable lighting and premium switches'),
                ('Wireless Gaming Mouse', 'Mice', 59.99, 40, 'mouse.jpg', 'High-precision wireless gaming mouse with 16000 DPI sensor'),
                ('Gaming Headset Pro', 'Audio', 129.99, 15, 'headset.jpg', '7.1 surround sound gaming headset with noise cancellation'),
                ('4K Gaming Monitor', 'Monitors', 399.99, 10, 'monitor.jpg', '27-inch 4K gaming monitor with 144Hz refresh rate'),
                ('Mechanical Keyswitch Set', 'Accessories', 34.99, 50, 'switches.jpg', 'Premium mechanical switches for keyboard customization'),
                ('Gaming Mouse Pad XXL', 'Accessories', 24.99, 60, 'mousepad.jpg', 'Extended gaming mouse pad with anti-slip base'),
                ('USB-C Hub 7-in-1', 'Accessories', 49.99, 30, 'hub.jpg', 'Multi-port USB-C hub with HDMI and card reader'),
                ('Webcam Full HD', 'Accessories', 79.99, 20, 'webcam.jpg', '1080p webcam with autofocus and built-in microphone'),
                ('Gaming Chair Pro', 'Furniture', 299.99, 8, 'chair.jpg', 'Ergonomic gaming chair with lumbar support and adjustable armrests'),
                ('Portable SSD 1TB', 'Storage', 119.99, 35, 'ssd.jpg', 'Ultra-fast portable SSD with USB 3.2 Gen 2'),
                ('Bluetooth Earbuds', 'Audio', 89.99, 45, 'earbuds.jpg', 'True wireless earbuds with active noise cancellation'),
                ('Gaming Laptop Cooling Pad', 'Accessories', 39.99, 28, 'coolingpad.jpg', 'RGB cooling pad with adjustable fan speeds')
            ]
            
            cursor.executemany('''
                INSERT INTO products (name, category, price, stock, image, description)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', sample_products)
            
            # Insert sample specs
            sample_specs = [
                (1, 'Switch Type: Cherry MX Red'), (1, 'Backlighting: RGB with 16.8M colors'),
                (1, 'Connection: USB-C'), (1, 'Key Rollover: N-key'),
                (2, 'Sensor: PixArt PMW3389'), (2, 'DPI Range: 100-16000'),
                (2, 'Battery Life: Up to 70 hours'), (2, 'Buttons: 8 programmable'),
                (3, 'Driver Size: 50mm'), (3, 'Frequency Response: 20Hz-20kHz'),
                (3, 'Microphone: Detachable noise-canceling'), (3, 'Connection: USB + 3.5mm'),
                (4, 'Resolution: 3840x2160 (4K UHD)'), (4, 'Refresh Rate: 144Hz'),
                (4, 'Response Time: 1ms GTG'), (4, 'Panel Type: IPS'),
            ]
            
            cursor.executemany('''
                INSERT INTO product_specs (product_id, spec)
                VALUES (?, ?)
            ''', sample_specs)

# User functions
def create_user(email, password, name, phone='', address=''):
    """Create a new user account"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        hashed_password = hash_password(password)
        try:
            cursor.execute('''
                INSERT INTO users (email, password, name, phone, address)
                VALUES (?, ?, ?, ?, ?)
            ''', (email, hashed_password, name, phone, address))
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            return None

def authenticate_user(email, password):
    """Authenticate user login"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        hashed_password = hash_password(password)
        cursor.execute('''
            SELECT * FROM users WHERE email = ? AND password = ?
        ''', (email, hashed_password))
        return cursor.fetchone()

def get_user_by_id(user_id):
    """Get user by ID"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        return cursor.fetchone()

def update_user_profile(user_id, name, phone, address):
    """Update user profile"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE users SET name = ?, phone = ?, address = ?
            WHERE id = ?
        ''', (name, phone, address, user_id))
        return cursor.rowcount > 0

# Product functions
def get_all_products():
    """Retrieve all products"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM products ORDER BY id DESC')
        return cursor.fetchall()

def get_products_by_category(category):
    """Retrieve products by category"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM products WHERE category = ? ORDER BY id DESC', (category,))
        return cursor.fetchall()

def get_product_by_id(product_id):
    """Retrieve single product by ID"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM products WHERE id = ?', (product_id,))
        return cursor.fetchone()

def get_product_specs(product_id):
    """Retrieve specifications for a product"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT spec FROM product_specs WHERE product_id = ?', (product_id,))
        return cursor.fetchall()

def get_categories():
    """Retrieve all unique categories"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT DISTINCT category FROM products ORDER BY category')
        return cursor.fetchall()

def get_featured_products(limit=8):
    """Retrieve featured products"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM products ORDER BY id DESC LIMIT ?', (limit,))
        return cursor.fetchall()

def search_products(query):
    """Search products by name or description"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        search_term = f'%{query}%'
        cursor.execute('''
            SELECT * FROM products 
            WHERE name LIKE ? OR description LIKE ?
            ORDER BY id DESC
        ''', (search_term, search_term))
        return cursor.fetchall()

# Order functions
def create_order(user_id, customer_name, customer_email, customer_phone, 
                 customer_address, total_amount, payment_method, notes=''):
    """Create a new order"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO orders (user_id, customer_name, customer_email, customer_phone,
                              customer_address, total_amount, payment_method, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, customer_name, customer_email, customer_phone, 
              customer_address, total_amount, payment_method, notes))
        return cursor.lastrowid

def add_order_item(order_id, product_id, product_name, quantity, price):
    """Add item to order"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO order_items (order_id, product_id, product_name, quantity, price)
            VALUES (?, ?, ?, ?, ?)
        ''', (order_id, product_id, product_name, quantity, price))
        return cursor.lastrowid

def get_user_orders(user_id):
    """Get all orders for a user"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM orders WHERE user_id = ?
            ORDER BY created_at DESC
        ''', (user_id,))
        return cursor.fetchall()

def get_all_orders():
    """Get all orders (admin)"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM orders ORDER BY created_at DESC')
        return cursor.fetchall()

def get_order_by_id(order_id):
    """Get order details"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM orders WHERE id = ?', (order_id,))
        return cursor.fetchone()

def get_order_items(order_id):
    """Get items in an order"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM order_items WHERE order_id = ?', (order_id,))
        return cursor.fetchall()

def update_order_status(order_id, status):
    """Update order status"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE orders SET status = ? WHERE id = ?
        ''', (status, order_id))
        return cursor.rowcount > 0

# Stock management
def check_stock(product_id, quantity):
    """Check if sufficient stock is available"""
    product = get_product_by_id(product_id)
    if product:
        return product['stock'] >= quantity
    return False

def update_stock(product_id, quantity):
    """Update product stock (can be negative for reduction)"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE products SET stock = stock + ? WHERE id = ?
        ''', (quantity, product_id))
        return cursor.rowcount > 0

# Admin product management
def add_product(name, category, price, stock, image, description):
    """Add a new product"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO products (name, category, price, stock, image, description)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (name, category, price, stock, image, description))
        return cursor.lastrowid

def update_product(product_id, name, category, price, stock, image, description):
    """Update existing product"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE products 
            SET name = ?, category = ?, price = ?, stock = ?, image = ?, description = ?
            WHERE id = ?
        ''', (name, category, price, stock, image, description, product_id))
        return cursor.rowcount > 0

def delete_product(product_id):
    """Delete a product"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM products WHERE id = ?', (product_id,))
        return cursor.rowcount > 0