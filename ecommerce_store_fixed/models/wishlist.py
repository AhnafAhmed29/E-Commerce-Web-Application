"""
Wishlist Model
Stores user's favorite products
"""
from models.db import db
from datetime import datetime


class Wishlist(db.Model):
    """Wishlist model - stores user's favorite products"""
    __tablename__ = 'wishlists'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('wishlist_items', lazy=True))
    product = db.relationship('Product', backref=db.backref('wishlisted_by', lazy=True))
    
    # Unique constraint - user can't add same product twice
    __table_args__ = (db.UniqueConstraint('user_id', 'product_id', name='unique_wishlist_item'),)
    
    def __repr__(self):
        return f'<Wishlist user={self.user_id} product={self.product_id}>'
