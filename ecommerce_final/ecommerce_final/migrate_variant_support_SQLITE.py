"""
Database Migration: Add Variant Support to Cart and Orders (SQLite Compatible)
Run this BEFORE implementing other fixes
"""
from app import app
from models.db import db
import sqlite3

def column_exists(table_name, column_name):
    """Check if column exists in table"""
    with app.app_context():
        try:
            result = db.session.execute(db.text(f"PRAGMA table_info({table_name})"))
            columns = [row[1] for row in result]
            return column_name in columns
        except Exception as e:
            print(f"Error checking column: {e}")
            return False

def migrate_add_variant_fields():
    """Add variant_id and variant_attributes to cart_items and order_items"""
    with app.app_context():
        print("="*60)
        print("STARTING VARIANT SYSTEM DATABASE MIGRATION (SQLite)")
        print("="*60)
        
        # Add variant fields to cart_items
        print("\n[1/4] Checking cart_items table...")
        
        try:
            # Check if variant_id exists
            if not column_exists('cart_items', 'variant_id'):
                print("  Adding variant_id column to cart_items...")
                db.session.execute(db.text("ALTER TABLE cart_items ADD COLUMN variant_id INTEGER"))
                db.session.commit()
                print("  ✅ variant_id added")
            else:
                print("  ⚠️  variant_id already exists, skipping")
        except Exception as e:
            print(f"  ❌ Error adding variant_id: {e}")
            db.session.rollback()
            return False
        
        try:
            # Check if variant_attributes exists
            if not column_exists('cart_items', 'variant_attributes'):
                print("  Adding variant_attributes column to cart_items...")
                db.session.execute(db.text("ALTER TABLE cart_items ADD COLUMN variant_attributes TEXT"))
                db.session.commit()
                print("  ✅ variant_attributes added")
            else:
                print("  ⚠️  variant_attributes already exists, skipping")
        except Exception as e:
            print(f"  ❌ Error adding variant_attributes: {e}")
            db.session.rollback()
            return False
        
        print("✅ Cart items table updated successfully")
        
        # Add variant fields to order_items
        print("\n[2/4] Checking order_items table...")
        
        try:
            # Check if variant_id exists
            if not column_exists('order_items', 'variant_id'):
                print("  Adding variant_id column to order_items...")
                db.session.execute(db.text("ALTER TABLE order_items ADD COLUMN variant_id INTEGER"))
                db.session.commit()
                print("  ✅ variant_id added")
            else:
                print("  ⚠️  variant_id already exists, skipping")
        except Exception as e:
            print(f"  ❌ Error adding variant_id: {e}")
            db.session.rollback()
            return False
        
        try:
            # Check if variant_attributes exists
            if not column_exists('order_items', 'variant_attributes'):
                print("  Adding variant_attributes column to order_items...")
                db.session.execute(db.text("ALTER TABLE order_items ADD COLUMN variant_attributes TEXT"))
                db.session.commit()
                print("  ✅ variant_attributes added")
            else:
                print("  ⚠️  variant_attributes already exists, skipping")
        except Exception as e:
            print(f"  ❌ Error adding variant_attributes: {e}")
            db.session.rollback()
            return False
        
        print("✅ Order items table updated successfully")
        
        # Verify the changes
        print("\n[3/4] Verifying cart_items columns...")
        try:
            result = db.session.execute(db.text("PRAGMA table_info(cart_items)"))
            columns = [row[1] for row in result]
            print(f"  Columns: {', '.join(columns)}")
            if 'variant_id' in columns and 'variant_attributes' in columns:
                print("  ✅ Verification passed")
            else:
                print("  ❌ Verification failed - columns missing")
                return False
        except Exception as e:
            print(f"  ❌ Error verifying: {e}")
            return False
        
        print("\n[4/4] Verifying order_items columns...")
        try:
            result = db.session.execute(db.text("PRAGMA table_info(order_items)"))
            columns = [row[1] for row in result]
            print(f"  Columns: {', '.join(columns)}")
            if 'variant_id' in columns and 'variant_attributes' in columns:
                print("  ✅ Verification passed")
            else:
                print("  ❌ Verification failed - columns missing")
                return False
        except Exception as e:
            print(f"  ❌ Error verifying: {e}")
            return False
        
        print("\n" + "="*60)
        print("🎉 MIGRATION COMPLETED SUCCESSFULLY!")
        print("="*60)
        print("\n📝 Next steps:")
        print("1. Update CartItem model (models/order.py)")
        print("2. Update OrderItem model (models/order.py)")
        print("3. Update add_to_cart route (app.py)")
        print("4. Add JavaScript to product page")
        print("\n")
        return True

if __name__ == '__main__':
    success = migrate_add_variant_fields()
    if not success:
        print("\n⚠️  Migration failed! Please check errors above.")
        exit(1)
    else:
        print("✅ You can now proceed to Phase 2: Update Models")
        exit(0)
