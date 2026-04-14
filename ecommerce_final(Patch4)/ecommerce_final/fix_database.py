"""
DATABASE FIX SCRIPT
This script recreates the database with the fixed SKU field (no unique constraint)
Run this to fix the UNIQUE constraint error
"""

from app import app
from models.db import db
from models.product import Product, Category, Brand
from models.user import User
from models.order import Order
from werkzeug.security import generate_password_hash

print("=" * 60)
print("DATABASE FIX SCRIPT - Remove SKU Unique Constraint")
print("=" * 60)
print()

with app.app_context():
    print("⚠️  WARNING: This will delete all existing data!")
    print("    Make sure you have backups if needed.")
    print()
    
    response = input("Do you want to continue? (yes/no): ")
    
    if response.lower() != 'yes':
        print("❌ Cancelled. No changes made.")
        exit()
    
    print()
    print("🗑️  Dropping all tables...")
    db.drop_all()
    print("✅ All tables dropped")
    
    print()
    print("🔨 Creating new tables with fixed schema...")
    db.create_all()
    print("✅ Tables created with SKU field (no unique constraint)")
    
    print()
    print("👤 Creating admin user...")
    admin = User(
        email='admin@ezgadgets.com',
        first_name='Admin',
        last_name='User',
        phone='01819940370'
    )
    admin.set_password('admin123')
    admin.admin = True
    db.session.add(admin)
    
    print()
    print("👤 Creating customer user...")
    customer = User(
        email='customer@example.com',
        first_name='Customer',
        last_name='User',
        phone='01234567890'
    )
    customer.set_password('customer123')
    db.session.add(customer)
    
    print()
    print("📁 Creating categories...")
    categories_data = [
        {'name': 'Keyboards', 'slug': 'keyboards'},
        {'name': 'Mice', 'slug': 'mice'},
        {'name': 'Monitors', 'slug': 'monitors'},
        {'name': 'Audio', 'slug': 'audio'},
        {'name': 'Accessories', 'slug': 'accessories'},
        {'name': 'Storage', 'slug': 'storage'},
        {'name': 'Furniture', 'slug': 'furniture'},
        {'name': 'Gamepad', 'slug': 'gamepad'}
    ]
    
    for cat_data in categories_data:
        category = Category(**cat_data)
        db.session.add(category)
    
    print()
    print("🏢 Creating brands...")
    brands_data = [
        {'name': '8BitDo', 'slug': '8bitdo'},
        {'name': 'Bigbigwon', 'slug': 'bigbigwon'},
        {'name': 'Aula', 'slug': 'aula'},
        {'name': 'Lingbao', 'slug': 'lingbao'},
        {'name': 'Marvo', 'slug': 'marvo'},
        {'name': 'EWEADN', 'slug': 'eweadn'},
        {'name': 'ATK', 'slug': 'atk'},
        {'name': 'Samsung', 'slug': 'samsung'}
    ]
    
    for brand_data in brands_data:
        brand = Brand(**brand_data)
        db.session.add(brand)
    
    db.session.commit()
    print("✅ Base data created")
    
    print()
    print("=" * 60)
    print("✅ DATABASE FIXED SUCCESSFULLY!")
    print("=" * 60)
    print()
    print("📊 Summary:")
    print(f"   • Admin User: admin@ezgadgets.com / admin123")
    print(f"   • Customer User: customer@example.com / customer123")
    print(f"   • Categories: {len(categories_data)} created")
    print(f"   • Brands: {len(brands_data)} created")
    print()
    print("🎯 Next Steps:")
    print("   1. Restart Flask: python app.py")
    print("   2. Login as admin")
    print("   3. Add products - SKU field is now optional!")
    print("   4. Upload images - will work without errors!")
    print()
    print("=" * 60)
