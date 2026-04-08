"""
Facade Pattern implementation for simplifying complex subsystem interactions
This demonstrates the Facade (Structural) design pattern
"""
import json  # ← IMPORTANT: Add this import at the top of facade.py
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
        Enhanced search: searches in product name, description, and category
    
        Args:
            query: Search term
            page: Page number
            per_page: Items per page
        
        Returns:
            Pagination object with matching products
        """
        # CORRECT IMPORT - Category is in product.py, NOT category.py
        from models.product import Category
    
        search_term = f"%{query}%"
    
        # Join with Category table to search in category fields too
        return Product.query.join(
            Category, Product.category_id == Category.id, isouter=True
        ).filter(
            db.and_(
                Product.is_active == True,
                db.or_(
                    Product.name.ilike(search_term),        # Search in product name
                    Product.description.ilike(search_term),  # Search in description
                    Category.name.ilike(search_term),        # Search in category name
                    Category.slug.ilike(search_term)         # Search in category slug
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
    def add_to_cart(cart, product_id, quantity=1, variant_id=None, variant_attributes=None):
        """
        Add product to cart WITH VARIANT SUPPORT (SQLite-Compatible)
        
        Args:
            cart: Cart object
            product_id: Product ID
            quantity: Quantity to add
            variant_id: Selected variant ID (optional)
            variant_attributes: Dict of variant attributes (optional)
        """
        from models.product import Product
        from models.order import CartItem  # ← Make sure this import is correct
        from models.product_variant import ProductVariant
        from models.db import db
        
        product = Product.query.get(product_id)
        if not product:
            return False, "Product not found"
        
        if not product.is_active:
            return False, "Product is not available"
        
        # ✨ Check stock (variant-specific if applicable)
        available_stock = product.stock
        if variant_id:
            variant = ProductVariant.query.get(variant_id)
            if variant:
                available_stock = variant.stock
                if not variant.is_active:
                    return False, "This variant is not available"
        
        if available_stock < quantity:
            return False, f"Only {available_stock} items available"
        
        # ✨ Check if item already in cart WITH SAME VARIANT
        existing_item = None
        for item in cart.items:
            if item.product_id == product_id:
                # Check if variants match
                if variant_id:
                    if item.variant_id == variant_id:
                        existing_item = item
                        break
                elif not item.variant_id:
                    # No variant specified, and item has no variant
                    existing_item = item
                    break
        
        if existing_item:
            # Update quantity
            new_quantity = existing_item.quantity + quantity
            if available_stock < new_quantity:
                return False, f"Only {available_stock} items available"
            existing_item.quantity = new_quantity
        else:
            # ✨ Create new cart item WITH VARIANT
            # IMPORTANT FOR SQLITE: Convert dict to JSON string
            variant_attrs_json = json.dumps(variant_attributes) if variant_attributes else None
            
            cart_item = CartItem(
                cart_id=cart.id,
                product_id=product_id,
                quantity=quantity,
                variant_id=variant_id,
                variant_attributes=variant_attrs_json  # ← JSON string, not dict
            )
            db.session.add(cart_item)
        
        try:
            db.session.commit()
            
            # Build message with variant info
            variant_info = ""
            if variant_attributes:
                parts = [f"{k.title()}: {v}" for k, v in variant_attributes.items()]
                variant_info = f" ({', '.join(parts)})"
            
            return True, f"{product.name}{variant_info} added to cart"
        except Exception as e:
            db.session.rollback()
            return False, f"Error adding to cart: {str(e)}"
    
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
    
    @staticmethod
    def transfer_cart_to_order(cart, order):
        """
        Transfer cart items to order items (with variant support)
        """
        from models.order import OrderItem
        from models.db import db
    
        for cart_item in cart.items:
            import json  # Add at top of file if not already there

            order_item = OrderItem(
                order_id=order.id,
                product_id=cart_item.product_id,
                product_name=cart_item.product.name,
                price=cart_item.unit_price,  # ← Use unit_price (includes variant)
                quantity=cart_item.quantity,
                variant_id=cart_item.variant_id,  # ← Add variant_id
                variant_attributes=cart_item.variant_attributes  # ← Add variant_attributes
            )
            db.session.add(order_item)
    
        try:
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Error transferring cart to order: {e}")
            return False



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
            
            # Create order items from cart WITH VARIANT SUPPORT
            for cart_item in cart.items:
                order_item = OrderItem(
                    order=order,
                    product_id=cart_item.product_id,
                    product_name=cart_item.product.name,
                    price=cart_item.unit_price,  # ✅ FIXED - includes variant price
                    quantity=cart_item.quantity,
                    variant_id=cart_item.variant_id,  # ✅ NEW - save variant
                    variant_attributes=cart_item.variant_attributes  # ✅ NEW - save variant attributes
                )
                db.session.add(order_item)
    
                # Update stock (variant-specific if applicable)
                if cart_item.variant_id:
                    # Deduct from variant stock
                    cart_item.variant.stock -= cart_item.quantity
                else:
                    # Deduct from product stock
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
