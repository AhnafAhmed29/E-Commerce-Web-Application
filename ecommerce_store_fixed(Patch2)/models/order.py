"""
Order and Cart models for ecommerce transactions
"""
from datetime import datetime
from models.db import db

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
    """
    __tablename__ = 'cart_items'
    
    id = db.Column(db.Integer, primary_key=True)
    cart_id = db.Column(db.Integer, db.ForeignKey('carts.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    
    # Relationship
    product = db.relationship('Product')
    
    def get_subtotal(self):
        """Calculate item subtotal"""
        return self.product.price * self.quantity
    
    def __repr__(self):
        return f'<CartItem {self.product.name} x{self.quantity}>'


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
    """
    __tablename__ = 'order_items'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    
    product_name = db.Column(db.String(200))  # Store name in case product is deleted
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, default=1)
    
    # Relationship
    product = db.relationship('Product')
    
    def get_subtotal(self):
        """Calculate item subtotal"""
        return self.price * self.quantity
    
    def __repr__(self):
        return f'<OrderItem {self.product_name} x{self.quantity}>'
