# COMPLETE SQLITE-COMPATIBLE MODELS
# File: models/order.py
# REPLACE your existing CartItem and OrderItem classes with these

"""
Order and Cart models for ecommerce transactions
SQLite-Compatible Version with Variant Support
"""
from datetime import datetime
from models.db import db
from models.product_variant import ProductVariant
import json  # ← IMPORTANT: Add this import


class Cart(db.Model):
    """
    Shopping cart for storing temporary user selections
    """
    __tablename__ = 'carts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    session_id = db.Column(db.String(100), nullable=True)  # For guest users
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    items = db.relationship('CartItem', backref='cart', lazy='dynamic', cascade='all, delete-orphan')
    
    def get_total(self):
        """Calculate cart total"""
        return sum(item.get_subtotal() for item in self.items)
    
    def get_item_count(self):
        """Get total number of items in cart"""
        return sum(item.quantity for item in self.items)
    
    def __repr__(self):
        return f'<Cart {self.id}>'


class CartItem(db.Model):
    """
    Individual items in shopping cart
    WITH VARIANT SUPPORT (SQLite-Compatible)
    """
    __tablename__ = 'cart_items'
    
    id = db.Column(db.Integer, primary_key=True)
    cart_id = db.Column(db.Integer, db.ForeignKey('carts.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    
    # ✨ NEW: Variant Support (SQLite uses Text for JSON)
    variant_id = db.Column(db.Integer, db.ForeignKey('product_variants.id'), nullable=True)
    variant_attributes = db.Column(db.Text, nullable=True)  # SQLite: Text instead of JSON
    
    # Relationships
    product = db.relationship('Product')
    variant = db.relationship('ProductVariant', backref='cart_items', foreign_keys=[variant_id])
    
    @property
    def unit_price(self):
        """
        Get unit price including ALL independent attribute modifiers.
        Option A: color modifier + edition modifier are summed independently,
        so a cart item with {"color": "Red", "edition": "Pro"} adds both
        price_modifiers from their respective variant rows.
        """
        base_price = self.product.price
        if not self.variant_attributes:
            return base_price
        try:
            attrs = json.loads(self.variant_attributes)
            if not attrs:
                return base_price
            total_modifier = 0.0
            matched_keys = set()
            for variant in self.product.variants:
                if not variant.attributes or not variant.is_active:
                    continue
                for attr_key, attr_value in variant.attributes.items():
                    if attr_key not in matched_keys and attrs.get(attr_key) == attr_value:
                        total_modifier += variant.price_modifier
                        matched_keys.add(attr_key)
                        break  # count each variant row only once
            return base_price + total_modifier
        except (json.JSONDecodeError, TypeError):
            return base_price
    
    @property
    def variant_display(self):
        """Get human-readable variant description"""
        if not self.variant_attributes:
            return None
        try:
            # Parse JSON string to dict
            attributes = json.loads(self.variant_attributes)
            parts = []
            for key, value in attributes.items():
                parts.append(f"{key.title()}: {value}")
            return " | ".join(parts)
        except (json.JSONDecodeError, TypeError, AttributeError):
            return None
    
    def get_subtotal(self):
        """Calculate item subtotal with variant price"""
        return self.unit_price * self.quantity
    
    def __repr__(self):
        variant_info = f" ({self.variant_display})" if self.variant_display else ""
        return f'<CartItem {self.product.name}{variant_info} x{self.quantity}>'


class Order(db.Model):
    """
    Order model for completed purchases
    """
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(50), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Order status
    status = db.Column(db.String(50), default='pending')  # pending, processing, shipped, delivered, cancelled
    payment_status = db.Column(db.String(50), default='pending')  # pending, paid, failed
    payment_method = db.Column(db.String(50))  # cod, bank_transfer, online
    
    # Shipping information
    shipping_first_name = db.Column(db.String(50))
    shipping_last_name = db.Column(db.String(50))
    shipping_company = db.Column(db.String(100))
    shipping_street = db.Column(db.String(200))
    shipping_apartment = db.Column(db.String(100))
    shipping_city = db.Column(db.String(100))
    shipping_district = db.Column(db.String(100))
    shipping_postcode = db.Column(db.String(20))
    shipping_phone = db.Column(db.String(20))
    shipping_email = db.Column(db.String(120))
    
    # Pricing
    subtotal = db.Column(db.Float, nullable=False)
    shipping_cost = db.Column(db.Float, default=60.0)
    total = db.Column(db.Float, nullable=False)
    
    # Notes
    order_notes = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    items = db.relationship('OrderItem', backref='order', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Order {self.order_number}>'


class OrderItem(db.Model):
    """
    Individual items in an order
    WITH VARIANT SUPPORT (SQLite-Compatible)
    """
    __tablename__ = 'order_items'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    
    product_name = db.Column(db.String(200))  # Store name in case product is deleted
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, default=1)
    
    # ✨ NEW: Variant Support (SQLite uses Text for JSON)
    variant_id = db.Column(db.Integer, db.ForeignKey('product_variants.id'), nullable=True)
    variant_attributes = db.Column(db.Text, nullable=True)  # SQLite: Text instead of JSON
    
    # Relationships
    product = db.relationship('Product')
    variant = db.relationship('ProductVariant', backref='order_items', foreign_keys=[variant_id])
    
    @property
    def variant_display(self):
        """Get human-readable variant description"""
        if not self.variant_attributes:
            return "Standard"
        try:
            # Parse JSON string to dict
            attributes = json.loads(self.variant_attributes)
            parts = []
            for key, value in attributes.items():
                parts.append(f"{key.title()}: {value}")
            return " | ".join(parts)
        except (json.JSONDecodeError, TypeError, AttributeError):
            return "Standard"
    
    def get_subtotal(self):
        """Calculate item subtotal"""
        return self.price * self.quantity
    
    def __repr__(self):
        variant_info = f" ({self.variant_display})" if self.variant_attributes else ""
        return f'<OrderItem {self.product_name}{variant_info} x{self.quantity}>'