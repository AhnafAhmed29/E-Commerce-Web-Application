"""
Product Variant Model - for Color, Edition, Size, etc.
Allows products to have multiple options with different prices/stock
"""
from models.db import db
from datetime import datetime


class ProductAttribute(db.Model):
    """
    Product Attribute Types (e.g., Color, Edition, Size)
    This defines what kind of options a product can have
    """
    __tablename__ = 'product_attributes'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)  # e.g., "color", "edition"
    display_name = db.Column(db.String(100))  # e.g., "Color", "Edition"
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    options = db.relationship('ProductAttributeOption', backref='attribute', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<ProductAttribute {self.name}>'


class ProductAttributeOption(db.Model):
    """
    Product Attribute Options (e.g., Red, Blue, Green for Color)
    These are the actual values for each attribute type
    """
    __tablename__ = 'product_attribute_options'
    
    id = db.Column(db.Integer, primary_key=True)
    attribute_id = db.Column(db.Integer, db.ForeignKey('product_attributes.id'), nullable=False)
    value = db.Column(db.String(100), nullable=False)  # e.g., "Red", "Standard Edition"
    price_modifier = db.Column(db.Float, default=0.0)  # Additional price for this option (+ or -)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<ProductAttributeOption {self.value}>'


class ProductVariant(db.Model):
    """
    Product Variants (specific combinations of attributes)
    Example: "Red + Pro Edition" or "Blue + Standard Edition"
    Each variant can have its own SKU, price, and stock
    """
    __tablename__ = 'product_variants'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    sku = db.Column(db.String(100), unique=True, nullable=True)
    price_modifier = db.Column(db.Float, default=0.0)  # Price difference from base product
    stock = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Store variant attributes as JSON
    # Example: {"color": "Red", "edition": "Pro"}
    attributes = db.Column(db.JSON)
    
    @property
    def full_price(self):
        """Get full price including modifier"""
        return self.product.price + self.price_modifier if self.product else self.price_modifier
    
    @property
    def display_name(self):
        """Get display name for this variant"""
        if not self.attributes:
            return "Default"
        return " - ".join([f"{k.title()}: {v}" for k, v in self.attributes.items()])
    
    def __repr__(self):
        return f'<ProductVariant {self.sku or self.id}>'


# Helper function to initialize default attributes
def init_default_attributes(db_session):
    """Create default Color and Edition attributes if they don't exist"""
    # Check if attributes already exist
    if ProductAttribute.query.count() > 0:
        return
    
    # Create Color attribute
    color_attr = ProductAttribute(
        name='color',
        display_name='Color'
    )
    db_session.add(color_attr)
    
    # Create Edition attribute
    edition_attr = ProductAttribute(
        name='edition',
        display_name='Edition'
    )
    db_session.add(edition_attr)
    
    db_session.commit()
    
    # Add some default color options
    default_colors = ['Black', 'White', 'Red', 'Blue', 'Green']
    for color in default_colors:
        option = ProductAttributeOption(
            attribute_id=color_attr.id,
            value=color,
            price_modifier=0.0
        )
        db_session.add(option)
    
    # Add some default edition options
    default_editions = ['Standard', 'Pro', 'Ultimate']
    for edition in default_editions:
        option = ProductAttributeOption(
            attribute_id=edition_attr.id,
            value=edition,
            price_modifier=0.0
        )
        db_session.add(option)
    
    db_session.commit()
    print("✅ Default attributes and options created!")
