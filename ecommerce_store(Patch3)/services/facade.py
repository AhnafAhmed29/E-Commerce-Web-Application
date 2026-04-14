"""
Facade Pattern implementation for simplifying complex subsystem interactions
This demonstrates the Facade (Structural) design pattern
"""
from models.db import db
from models.user import User, Address
from models.product import Product, Category, Brand
from models.order import Cart, CartItem, Order, OrderItem
from factories.user_factory import create_user
from strategies.auth_strategy import authenticate_user, authenticate_admin
from datetime import datetime
import secrets

class AuthServiceFacade:
    """
    Facade for authentication operations
    Simplifies user registration, login, and management
    """
    
    @staticmethod
    def register_user(email, username, password, user_type='customer', **kwargs):
        """
        Register a new user
        
        Returns:
            tuple: (success: bool, message: str, user: User or None)
        """
        try:
            # Check if email already exists
            if User.query.filter_by(email=email).first():
                return False, "Email already registered", None
            
            # Check if username already exists
            if User.query.filter_by(username=username).first():
                return False, "Username already taken", None
            
            # Create user using Factory pattern
            user = create_user(email, username, password, user_type, **kwargs)
            
            # Save to database
            db.session.add(user)
            db.session.commit()
            
            return True, "Registration successful", user
            
        except Exception as e:
            db.session.rollback()
            return False, f"Registration failed: {str(e)}", None
    
    @staticmethod
    def login_user(identifier, password, is_admin=False):
        """
        Login user using Strategy pattern
        
        Returns:
            tuple: (success: bool, message: str, user: User or None)
        """
        try:
            # Use appropriate authentication strategy
            if is_admin:
                user = authenticate_admin(identifier, password)
            else:
                user = authenticate_user(identifier, password)
            
            if user:
                return True, "Login successful", user
            else:
                return False, "Invalid credentials", None
                
        except Exception as e:
            return False, f"Login failed: {str(e)}", None
    
    @staticmethod
    def get_user_by_id(user_id):
        """Get user by ID"""
        return User.query.get(user_id)


class ProductServiceFacade:
    """
    Facade for product operations
    Simplifies product catalog management
    """
    
    @staticmethod
    def get_all_products(page=1, per_page=12):
        """
        Get paginated products
        
        Returns:
            Pagination object
        """
        return Product.query.filter_by(is_active=True).paginate(
            page=page, per_page=per_page, error_out=False
        )
    
    @staticmethod
    def get_product_by_slug(slug):
        """Get single product by slug"""
        return Product.query.filter_by(slug=slug, is_active=True).first()
    
    @staticmethod
    def get_product_by_id(product_id):
        """Get single product by ID"""
        return Product.query.get(product_id)
    
    @staticmethod
    def search_products(query, page=1, per_page=12):
        """
        Search products by name or description
        
        Returns:
            Pagination object
        """
        search_term = f"%{query}%"
        return Product.query.filter(
            db.and_(
                Product.is_active == True,
                db.or_(
                    Product.name.ilike(search_term),
                    Product.description.ilike(search_term)
                )
            )
        ).paginate(page=page, per_page=per_page, error_out=False)
    
    @staticmethod
    def get_products_by_category(category_slug, page=1, per_page=12):
        """
        Get products by category
        
        Returns:
            Pagination object
        """
        category = Category.query.filter_by(slug=category_slug).first()
        if not category:
            return None
        
        return Product.query.filter_by(
            category_id=category.id,
            is_active=True
        ).paginate(page=page, per_page=per_page, error_out=False)
    
    @staticmethod
    def get_featured_products(limit=8):
        """Get featured products"""
        return Product.query.filter_by(
            is_featured=True,
            is_active=True
        ).limit(limit).all()
    
    @staticmethod
    def get_new_products(limit=10):
        """Get new products"""
        return Product.query.filter_by(
            is_new=True,
            is_active=True
        ).order_by(Product.created_at.desc()).limit(limit).all()
    
    @staticmethod
    def get_categories():
        """Get all categories"""
        return Category.query.all()
    
    @staticmethod
    def get_brands():
        """Get all brands"""
        return Brand.query.all()


class CartServiceFacade:
    """
    Facade for shopping cart operations
    Simplifies cart management
    """
    
    @staticmethod
    def get_or_create_cart(user_id=None, session_id=None):
        """
        Get existing cart or create new one
        
        Returns:
            Cart object
        """
        if user_id:
            cart = Cart.query.filter_by(user_id=user_id).first()
        elif session_id:
            cart = Cart.query.filter_by(session_id=session_id).first()
        else:
            return None
        
        if not cart:
            cart = Cart(user_id=user_id, session_id=session_id)
            db.session.add(cart)
            db.session.commit()
        
        return cart
    
    @staticmethod
    def add_to_cart(cart, product_id, quantity=1):
        """
        Add item to cart
        
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            product = Product.query.get(product_id)
            if not product:
                return False, "Product not found"
            
            if product.stock < quantity:
                return False, "Insufficient stock"
            
            # Check if item already in cart
            cart_item = CartItem.query.filter_by(
                cart_id=cart.id,
                product_id=product_id
            ).first()
            
            if cart_item:
                cart_item.quantity += quantity
            else:
                cart_item = CartItem(
                    cart_id=cart.id,
                    product_id=product_id,
                    quantity=quantity
                )
                db.session.add(cart_item)
            
            db.session.commit()
            return True, "Added to cart"
            
        except Exception as e:
            db.session.rollback()
            return False, f"Error: {str(e)}"
    
    @staticmethod
    def update_cart_item(cart_item_id, quantity):
        """
        Update cart item quantity
        
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            cart_item = CartItem.query.get(cart_item_id)
            if not cart_item:
                return False, "Item not found"
            
            if quantity <= 0:
                db.session.delete(cart_item)
            else:
                if cart_item.product.stock < quantity:
                    return False, "Insufficient stock"
                cart_item.quantity = quantity
            
            db.session.commit()
            return True, "Cart updated"
            
        except Exception as e:
            db.session.rollback()
            return False, f"Error: {str(e)}"
    
    @staticmethod
    def remove_from_cart(cart_item_id):
        """
        Remove item from cart
        
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            cart_item = CartItem.query.get(cart_item_id)
            if cart_item:
                db.session.delete(cart_item)
                db.session.commit()
                return True, "Item removed"
            return False, "Item not found"
            
        except Exception as e:
            db.session.rollback()
            return False, f"Error: {str(e)}"
    
    @staticmethod
    def clear_cart(cart):
        """Clear all items from cart"""
        try:
            CartItem.query.filter_by(cart_id=cart.id).delete()
            db.session.commit()
            return True, "Cart cleared"
        except Exception as e:
            db.session.rollback()
            return False, f"Error: {str(e)}"


class OrderServiceFacade:
    """
    Facade for order operations
    Simplifies order creation and management
    """
    
    @staticmethod
    def create_order(user, cart, shipping_data, payment_method='cod', order_notes=''):
        """
        Create order from cart
        
        Returns:
            tuple: (success: bool, message: str, order: Order or None)
        """
        try:
            if not cart.items.count():
                return False, "Cart is empty", None
            
            # Generate order number
            order_number = f"ORD-{datetime.now().strftime('%Y%m%d')}-{secrets.token_hex(4).upper()}"
            
            # Calculate totals
            subtotal = cart.get_total()
            shipping_cost = 60.0  # Fixed shipping cost
            total = subtotal + shipping_cost
            
            # Create order
            order = Order(
                order_number=order_number,
                user_id=user.id,
                payment_method=payment_method,
                subtotal=subtotal,
                shipping_cost=shipping_cost,
                total=total,
                order_notes=order_notes,
                **shipping_data
            )
            
            db.session.add(order)
            
            # Create order items from cart
            for cart_item in cart.items:
                order_item = OrderItem(
                    order=order,
                    product_id=cart_item.product_id,
                    product_name=cart_item.product.name,
                    price=cart_item.product.price,
                    quantity=cart_item.quantity
                )
                db.session.add(order_item)
                
                # Update product stock
                cart_item.product.stock -= cart_item.quantity
            
            # Clear cart
            CartItem.query.filter_by(cart_id=cart.id).delete()
            
            db.session.commit()
            return True, "Order placed successfully", order
            
        except Exception as e:
            db.session.rollback()
            return False, f"Order failed: {str(e)}", None
    
    @staticmethod
    def get_user_orders(user_id):
        """Get all orders for a user"""
        return Order.query.filter_by(user_id=user_id).order_by(
            Order.created_at.desc()
        ).all()
    
    @staticmethod
    def get_order_by_id(order_id):
        """Get order by ID"""
        return Order.query.get(order_id)
