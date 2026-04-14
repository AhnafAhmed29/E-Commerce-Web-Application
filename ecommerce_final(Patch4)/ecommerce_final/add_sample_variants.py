"""
Add sample variants to products
Run this to populate color/edition options
"""
from app import app
from models.db import db
from models.product import Product
from models.product_variant import ProductVariant

with app.app_context():
    # Get all products
    products = Product.query.all()
    
    for product in products[:5]:  # First 5 products
        print(f"Adding variants to: {product.name}")
        
        # Add Black color variant
        variant1 = ProductVariant(
            product_id=product.id,
            sku=f"{product.id}-black",
            attributes={"color": "Black"},
            price_modifier=0.0,
            stock=50
        )
        db.session.add(variant1)
        
        # Add White color variant  
        variant2 = ProductVariant(
            product_id=product.id,
            sku=f"{product.id}-white",
            attributes={"color": "White"},
            price_modifier=0.0,
            stock=30
        )
        db.session.add(variant2)
        
        # Add Red color variant with extra cost
        variant3 = ProductVariant(
            product_id=product.id,
            sku=f"{product.id}-red",
            attributes={"color": "Red"},
            price_modifier=200.0,  # +200 BDT
            stock=20
        )
        db.session.add(variant3)
        
        # Add Standard Edition
        variant4 = ProductVariant(
            product_id=product.id,
            sku=f"{product.id}-standard",
            attributes={"edition": "Standard"},
            price_modifier=0.0,
            stock=100
        )
        db.session.add(variant4)
        
        # Add Pro Edition
        variant5 = ProductVariant(
            product_id=product.id,
            sku=f"{product.id}-pro",
            attributes={"edition": "Pro"},
            price_modifier=500.0,  # +500 BDT
            stock=50
        )
        db.session.add(variant5)
    
    db.session.commit()
    print("\n✅ Sample variants added to first 5 products!")
    print("✅ View any product page to see Color and Edition dropdowns!")