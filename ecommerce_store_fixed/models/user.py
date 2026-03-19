"""
User model for authentication and user management
"""
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from models.db import db

class User(UserMixin, db.Model):
    """
    User model representing registered users
    Implements UserMixin for Flask-Login integration
    """
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    phone = db.Column(db.String(20))
    
    # User type (for Factory Pattern)
    user_type = db.Column(db.String(20), default='customer')  # 'customer' or 'admin'
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    orders = db.relationship('Order', backref='user', lazy='dynamic')
    addresses = db.relationship('Address', backref='user', lazy='dynamic')
    
    def __init__(self, email, username, password, user_type='customer', first_name='', last_name='', phone=''):
        """Initialize user with required fields"""
        self.email = email
        self.username = username
        self.set_password(password)
        self.user_type = user_type
        self.first_name = first_name
        self.last_name = last_name
        self.phone = phone
    
    def set_password(self, password):
        """Hash and set the user password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify password against hash"""
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        """Check if user is an admin"""
        return self.user_type == 'admin'
    
    def get_full_name(self):
        """Get user's full name"""
        return f"{self.first_name} {self.last_name}".strip() or self.username
    
    def __repr__(self):
        return f'<User {self.username}>'


class Address(db.Model):
    """
    Address model for user shipping/billing addresses
    """
    __tablename__ = 'addresses'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    company = db.Column(db.String(100))
    street_address = db.Column(db.String(200), nullable=False)
    apartment = db.Column(db.String(100))
    city = db.Column(db.String(100), nullable=False)
    district = db.Column(db.String(100))
    postcode = db.Column(db.String(20))
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    
    is_default = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Address {self.city}>'
