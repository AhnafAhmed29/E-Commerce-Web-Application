"""
Product model for the ecommerce catalog
"""
from datetime import datetime
from models.db import db

class Category(db.Model):
    """
    Category model for product categorization
    """
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    image = db.Column(db.String(200))
    parent_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    
    # Relationships
    products = db.relationship('Product', backref='category', lazy='dynamic')
    children = db.relationship('Category', backref=db.backref('parent', remote_side=[id]))
    
    def __repr__(self):
        return f'<Category {self.name}>'


class Brand(db.Model):
    """
    Brand model for product manufacturers
    """
    __tablename__ = 'brands'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    logo = db.Column(db.String(200))
    
    # Relationships
    products = db.relationship('Product', backref='brand', lazy='dynamic')
    
    def __repr__(self):
        return f'<Brand {self.name}>'


class Product(db.Model):
    """
    Product model representing items in the catalog
    """
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), unique=True, nullable=False)
    description = db.Column(db.Text)
    short_description = db.Column(db.String(500))
    
    # Pricing
    price = db.Column(db.Float, nullable=False)
    original_price = db.Column(db.Float)  # For showing discounts
    
    # Stock management
    stock = db.Column(db.Integer, default=0)
    sku = db.Column(db.String(100), nullable=True)  # Removed unique constraint
    
    # Images
    main_image = db.Column(db.String(200))
    image_2 = db.Column(db.String(200))
    image_3 = db.Column(db.String(200))
    image_4 = db.Column(db.String(200))
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    is_featured = db.Column(db.Boolean, default=False)
    is_new = db.Column(db.Boolean, default=False)
    is_hot = db.Column(db.Boolean, default=False)
    discount_percentage = db.Column(db.Integer, default=0)
    
    # Foreign Keys
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    brand_id = db.Column(db.Integer, db.ForeignKey('brands.id'))
    
    # Metadata
    warranty_period = db.Column(db.String(50))  # e.g., "1 Year"
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    specifications = db.relationship('ProductSpecification', backref='product', lazy='dynamic', cascade='all, delete-orphan')
    reviews = db.relationship('Review', backref='product', lazy='dynamic', cascade='all, delete-orphan')
    
    def __init__(self, name, slug, price, **kwargs):
        """Initialize product with required fields"""
        self.name = name
        self.slug = slug
        self.price = price
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    @property
    def is_in_stock(self):
        """Check if product is in stock"""
        return self.stock > 0
    
    @property
    def stock_status(self):
        """Get readable stock status"""
        if self.stock > 10:
            return "In Stock"
        elif self.stock > 0:
            return f"Only {self.stock} left"
        else:
            return "Out of Stock"
    
    @property
    def has_discount(self):
        """Check if product has a discount"""
        return self.original_price and self.original_price > self.price
    
    def get_discount_percentage(self):
        """Calculate discount percentage"""
        if self.has_discount:
            return int(((self.original_price - self.price) / self.original_price) * 100)
        return 0
    
    def get_images(self):
        """Get all product images as a list"""
        images = [self.main_image]
        if self.image_2:
            images.append(self.image_2)
        if self.image_3:
            images.append(self.image_3)
        if self.image_4:
            images.append(self.image_4)
        return [img for img in images if img]
    
    def __repr__(self):
        return f'<Product {self.name}>'


class ProductSpecification(db.Model):
    """
    Product specifications/features
    """
    __tablename__ = 'product_specifications'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    key = db.Column(db.String(100), nullable=False)
    value = db.Column(db.String(500), nullable=False)
    
    def __repr__(self):
        return f'<Spec {self.key}: {self.value}>'


class Review(db.Model):
    """
    Product reviews and ratings
    """
    __tablename__ = 'reviews'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    rating = db.Column(db.Integer, nullable=False)  # 1-5 stars
    title = db.Column(db.String(200))
    comment = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    user = db.relationship('User', backref='reviews')
    
    def __repr__(self):
        return f'<Review {self.rating} stars>'