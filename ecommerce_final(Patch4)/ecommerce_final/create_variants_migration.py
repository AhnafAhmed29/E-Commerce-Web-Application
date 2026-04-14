"""
Migration Script - Add Product Variants Support
Run this once to create variant tables and default data
"""
from app import app
from models.db import db
from models.product_variant import ProductAttribute, ProductAttributeOption, ProductVariant, init_default_attributes

def create_variant_tables():
    """Create all variant-related tables"""
    with app.app_context():
        print("Creating product variant tables...")
        
        # Create tables
        db.create_all()
        print("✅ Tables created!")
        
        # Initialize default attributes
        print("Creating default attributes (Color, Edition)...")
        init_default_attributes(db.session)
        print("✅ Default attributes created!")
        
        print("\n" + "="*50)
        print("🎉 MIGRATION COMPLETE!")
        print("="*50)
        print("\nYou can now:")
        print("1. Add color/edition options to products in admin")
        print("2. Products will show dropdown selectors on detail pages")
        print("3. Each variant can have different price/stock")
        print("\nDefault colors available: Black, White, Red, Blue, Green")
        print("Default editions available: Standard, Pro, Ultimate")
        print("\n")

if __name__ == '__main__':
    create_variant_tables()
