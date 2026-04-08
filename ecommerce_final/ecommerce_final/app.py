"""
Main Flask application file with routes
Integrates all design patterns and services
"""
from werkzeug.utils import secure_filename
from datetime import datetime
import os
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from config import config
from models.db import db_manager, db
from models.user import User
from models.product import Product, Category
from models.wishlist import Wishlist
from services.facade import (
    AuthServiceFacade,
    ProductServiceFacade,
    CartServiceFacade,
    OrderServiceFacade
)

import secrets
import re

# ==================== HELPERS ====================

def generate_slug(name):
    """
    Generate a unique, URL-safe, lowercase slug from a product name.
    Appends a short hex suffix if the slug already exists.
    """
    from models.product import Product
    # Lowercase and replace spaces/special chars with hyphens
    slug = re.sub(r'[^\w\s-]', '', name.lower())
    slug = re.sub(r'[\s_]+', '-', slug).strip('-')
    slug = re.sub(r'-+', '-', slug)

    # Ensure uniqueness
    base_slug = slug
    counter = 1
    while Product.query.filter_by(slug=slug).first():
        slug = f"{base_slug}-{secrets.token_hex(3)}"
        counter += 1
        if counter > 20:
            break
    return slug


# Create Flask app
app = Flask(__name__)

# Load configuration
env = os.environ.get('FLASK_ENV', 'development')
app.config.from_object(config[env])

# Initialize database (Singleton pattern)
db_manager.init_app(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'

@login_manager.user_loader
def load_user(user_id):
    """Load user for Flask-Login"""
    return AuthServiceFacade.get_user_by_id(int(user_id))


def get_variant_modifier(product, attribute_name, attribute_value):
    """Get price modifier for a specific variant attribute"""
    for variant in product.variants:
        if variant.attributes and variant.attributes.get(attribute_name) == attribute_value:
            return variant.price_modifier
    return 0.0

# Make it available in templates
app.jinja_env.globals.update(get_variant_modifier=get_variant_modifier)

# ==================== CONTEXT PROCESSORS ====================

@app.context_processor
def inject_globals():
    """Inject global variables into all templates"""
    cart = None
    cart_count = 0
    
    if current_user.is_authenticated:
        cart = CartServiceFacade.get_or_create_cart(user_id=current_user.id)
    elif 'session_id' in session:
        cart = CartServiceFacade.get_or_create_cart(session_id=session['session_id'])
    
    if cart:
        cart_count = cart.get_item_count()
    
    categories = ProductServiceFacade.get_categories()
    
    return {
        'cart_count': cart_count,
        'categories': categories
    }


# ==================== HOME & GENERAL ROUTES ====================

@app.route('/')
def index():
    """Home page with featured products"""
    featured_products = ProductServiceFacade.get_featured_products(limit=12)
    new_products = ProductServiceFacade.get_new_products(limit=10)
    categories = ProductServiceFacade.get_categories()
    
    return render_template('index.html',
                         featured_products=featured_products,
                         new_products=new_products,
                         categories=categories)


@app.route('/about')
def about():
    """About page"""
    return render_template('about.html')


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    """Contact page"""
    if request.method == 'POST':
        # Handle contact form submission
        flash('Thank you for contacting us! We will get back to you soon.', 'success')
        return redirect(url_for('contact'))
    
    return render_template('contact.html')


# ==================== AUTHENTICATION ROUTES ====================

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration using Factory pattern"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')
        first_name = request.form.get('first_name', '')
        last_name = request.form.get('last_name', '')
        phone = request.form.get('phone', '')
        
        # Use Facade to register user (which uses Factory internally)
        success, message, user = AuthServiceFacade.register_user(
            email, username, password,
            first_name=first_name,
            last_name=last_name,
            phone=phone
        )
        
        if success:
            flash(message, 'success')
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash(message, 'error')
    
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login route"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        identifier = request.form.get('identifier')  # email or phone
        password = request.form.get('password')
        remember = request.form.get('remember', False)
        
        # Use Facade to login (which uses Strategy pattern internally)
        success, message, user = AuthServiceFacade.login_user(identifier, password)
        
        if success:
            login_user(user, remember=remember)
            
            # Check for pending buy now AFTER successful login
            if 'pending_buy_now' in session:
                product_id = session.pop('pending_buy_now')
                quantity = session.pop('pending_quantity', 1)
                
                # Use CartServiceFacade to add to DATABASE cart
                cart = CartServiceFacade.get_or_create_cart(user_id=user.id)
                success_cart, message_cart = CartServiceFacade.add_to_cart(cart, product_id, quantity)
                
                if success_cart:
                    flash('Proceeding to checkout...', 'success')
                else:
                    flash(message_cart, 'error')
                
                return redirect(url_for('checkout'))
            
            # Normal login redirect (if no pending buy now)
            next_page = request.args.get('next')
            flash('Welcome back!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash(message, 'error')
    
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('index'))


# ==================== PRODUCT ROUTES ====================

@app.route('/products')
def products():
    """Product listing page with search, category filter, and all products"""
    page = request.args.get('page', 1, type=int)
    category_slug = request.args.get('category')
    search_query = request.args.get('q')
    
    # SEARCH RESULTS - Show flash message with count
    if search_query:
        products_page = ProductServiceFacade.search_products(search_query, page=page)
        page_title = f"Search results for '{search_query}'"
        
        # Flash message ONLY for search results
        if products_page.total == 0:
            flash(f'No products found for "{search_query}". Try different keywords.', 'info')
        else:
            flash(f'Found {products_page.total} product(s) for "{search_query}"', 'success')
    
    # CATEGORY FILTER - No flash message (user is browsing)
    elif category_slug:
        products_page = ProductServiceFacade.get_products_by_category(category_slug, page=page)
        page_title = category_slug.replace('-', ' ').title()
    
    # ALL PRODUCTS - No flash message (user is browsing)
    else:
        products_page = ProductServiceFacade.get_all_products(page=page)
        page_title = "All Products"
    
    return render_template('products.html',
                         products=products_page,
                         page_title=page_title)


@app.route('/product/<slug>')
def product_detail(slug):
    """Product detail page"""
    product = ProductServiceFacade.get_product_by_slug(slug)
    
    if not product:
        flash('Product not found', 'error')
        return redirect(url_for('products'))
    
    # Get related products from same category
    related_products = Product.query.filter(
        Product.category_id == product.category_id,
        Product.id != product.id,
        Product.is_active == True
    ).limit(4).all()
    
    return render_template('product.html',
                         product=product,
                         related_products=related_products)


@app.route('/category/<slug>')
def category(slug):
    """Category page"""
    return redirect(url_for('products', category=slug))



# ==================== CART ROUTES ====================

@app.route('/cart')
def cart():
    """Shopping cart page"""
    # Get or create cart
    if current_user.is_authenticated:
        cart_obj = CartServiceFacade.get_or_create_cart(user_id=current_user.id)
    else:
        if 'session_id' not in session:
            session['session_id'] = secrets.token_hex(16)
        cart_obj = CartServiceFacade.get_or_create_cart(session_id=session['session_id'])
    
    return render_template('cart.html', cart=cart_obj)


@app.route('/cart/add', methods=['POST'])
def add_to_cart():
    """Add product to cart WITH VARIANT SUPPORT"""
    product_id = request.form.get('product_id', type=int)
    quantity = request.form.get('quantity', 1, type=int)
    
    # ✨ NEW: Capture variant selection
    selected_color = request.form.get('color')
    selected_edition = request.form.get('edition')
    
    # Get or create cart
    if current_user.is_authenticated:
        cart_obj = CartServiceFacade.get_or_create_cart(user_id=current_user.id)
    else:
        if 'session_id' not in session:
            session['session_id'] = secrets.token_hex(16)
        cart_obj = CartServiceFacade.get_or_create_cart(session_id=session['session_id'])
    
    # Build variant attributes dict (Option A: independent modifiers)
    variant_attributes = {}
    if selected_color:
        variant_attributes['color'] = selected_color
    if selected_edition:
        variant_attributes['edition'] = selected_edition

    # Add to cart — no combined variant lookup needed.
    # CartItem.unit_price will sum all matching attribute modifiers.
    success, message = CartServiceFacade.add_to_cart(
        cart_obj,
        product_id,
        quantity,
        variant_id=None,
        variant_attributes=variant_attributes if variant_attributes else None
    )
    
    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')
    
    return redirect(request.referrer or url_for('products'))


@app.route('/cart/update/<int:item_id>', methods=['POST'])
def update_cart(item_id):
    """Update cart item quantity"""
    quantity = request.form.get('quantity', type=int)
    
    success, message = CartServiceFacade.update_cart_item(item_id, quantity)
    
    if request.is_json:
        return jsonify({'success': success, 'message': message})
    
    flash(message, 'success' if success else 'error')
    return redirect(url_for('cart'))


@app.route('/cart/remove/<int:item_id>')
def remove_from_cart(item_id):
    """Remove item from cart"""
    success, message = CartServiceFacade.remove_from_cart(item_id)
    flash(message, 'success' if success else 'error')
    return redirect(url_for('cart'))


# ==================== CHECKOUT & ORDER ROUTES ====================

@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    """Checkout page"""
    # Get cart
    cart_obj = CartServiceFacade.get_or_create_cart(user_id=current_user.id)
    
    if not cart_obj.items.count():
        flash('Your cart is empty', 'warning')
        return redirect(url_for('products'))
    
    if request.method == 'POST':
        # Collect shipping data
        shipping_data = {
            'shipping_first_name': request.form.get('first_name'),
            'shipping_last_name': request.form.get('last_name'),
            'shipping_company': request.form.get('company', ''),
            'shipping_street': request.form.get('street'),
            'shipping_apartment': request.form.get('apartment', ''),
            'shipping_city': request.form.get('city'),
            'shipping_district': request.form.get('district', ''),
            'shipping_postcode': request.form.get('postcode', ''),
            'shipping_phone': request.form.get('phone'),
            'shipping_email': request.form.get('email')
        }
        
        payment_method = request.form.get('payment_method', 'cod')
        order_notes = request.form.get('order_notes', '')
        
        # Create order using Facade
        success, message, order = OrderServiceFacade.create_order(
            current_user, cart_obj, shipping_data, payment_method, order_notes
        )
        
        if success:
            flash(f'Order {order.order_number} placed successfully!', 'success')
            return redirect(url_for('order_confirmation', order_id=order.id))
        else:
            flash(message, 'error')
    
    return render_template('checkout.html', cart=cart_obj)


@app.route('/order/<int:order_id>')
@login_required
def order_confirmation(order_id):
    """Order confirmation page"""
    order = OrderServiceFacade.get_order_by_id(order_id)
    
    if not order or order.user_id != current_user.id:
        flash('Order not found', 'error')
        return redirect(url_for('index'))
    
    return render_template('order_confirmation.html', order=order)


@app.route('/orders')
@login_required
def my_orders():
    """User's order history"""
    orders = OrderServiceFacade.get_user_orders(current_user.id)
    return render_template('orders.html', orders=orders)


# ==================== ADMIN ROUTES ====================

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    """Enhanced Admin Dashboard with status-based order sections"""
    if not current_user.is_admin():
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('index'))
    
    from models.order import Order
    from models.product import Product
    
    # Get statistics
    total_orders = Order.query.count()
    pending_orders_count = Order.query.filter_by(status='pending').count()
    processing_orders_count = Order.query.filter_by(status='processing').count()
    shipped_orders_count = Order.query.filter_by(status='shipped').count()
    delivered_orders_count = Order.query.filter_by(status='delivered').count()
    cancelled_orders_count = Order.query.filter_by(status='cancelled').count()
    
    total_products = Product.query.count()
    total_revenue = db.session.query(db.func.sum(Order.total)).filter(
        Order.status.in_(['delivered', 'shipped', 'processing'])
    ).scalar() or 0
    
    # Get ALL orders by status - DYNAMIC SECTIONS
    pending_orders = Order.query.filter_by(status='pending').order_by(
        Order.created_at.desc()
    ).all()
    
    processing_orders = Order.query.filter_by(status='processing').order_by(
        Order.created_at.desc()
    ).all()
    
    shipped_orders = Order.query.filter_by(status='shipped').order_by(
        Order.created_at.desc()
    ).all()
    
    delivered_orders = Order.query.filter_by(status='delivered').order_by(
        Order.created_at.desc()
    ).all()
    
    cancelled_orders = Order.query.filter_by(status='cancelled').order_by(
        Order.created_at.desc()
    ).all()
    
    return render_template('admin/dashboard.html',
                         total_orders=total_orders,
                         pending_orders_count=pending_orders_count,
                         processing_orders_count=processing_orders_count,
                         shipped_orders_count=shipped_orders_count,
                         delivered_orders_count=delivered_orders_count,
                         cancelled_orders_count=cancelled_orders_count,
                         total_products=total_products,
                         total_revenue=total_revenue,
                         pending_orders=pending_orders,
                         processing_orders=processing_orders,
                         shipped_orders=shipped_orders,
                         delivered_orders=delivered_orders,
                         cancelled_orders=cancelled_orders)


@app.route('/admin/order/<int:order_id>')
@login_required
def admin_order_detail(order_id):
    """View complete order details with customer info"""
    if not current_user.is_admin():
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('index'))
    
    from models.order import Order
    
    order = Order.query.get_or_404(order_id)
    
    return render_template('admin/order_detail.html', order=order)


@app.route('/admin/orders')
@login_required
def admin_orders():
    """Manage Orders - View all orders"""
    if not current_user.is_admin():
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('index'))
    
    from models.order import Order
    
    # Get all orders, newest first
    orders = Order.query.order_by(Order.created_at.desc()).all()
    
    return render_template('admin/orders.html', orders=orders)


@app.route('/admin/order/<int:order_id>/update-status', methods=['POST'])
@login_required
def admin_update_order_status(order_id):
    """Update order status"""
    if not current_user.is_admin():
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('index'))
    
    from models.order import Order
    
    order = Order.query.get_or_404(order_id)
    new_status = request.form.get('status')
    
    if new_status in ['pending', 'processing', 'shipped', 'delivered', 'cancelled']:
        order.status = new_status
        db.session.commit()
        flash(f'Order #{order.order_number} status updated to {new_status}!', 'success')
    else:
        flash('Invalid status', 'error')
    
    return redirect(url_for('admin_orders'))


@app.route('/admin/products')
@login_required
def admin_products():
    """Manage Products - View all products"""
    if not current_user.is_admin():
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('index'))
    
    from models.product import Product
    
    # Get all products
    products = Product.query.order_by(Product.created_at.desc()).all()
    
    return render_template('admin/products.html', products=products)


@app.route('/admin/products/add', methods=['GET', 'POST'])
@login_required
def admin_add_product():
    """Add new product"""
    if request.method == 'POST':
        try:
            # Get basic product data
            name = request.form.get('name')
            description = request.form.get('description')
            short_description = request.form.get('short_description', '')
            price = float(request.form.get('price', 0))
            stock = int(request.form.get('stock', 0))
            category_id = request.form.get('category_id', type=int)
            brand_id = request.form.get('brand_id', type=int)
            is_new = 'is_new' in request.form
            is_hot = 'is_hot' in request.form
            
            # Create product
            product = Product(
                name=name,
                slug=generate_slug(name),
                description=description,
                short_description=short_description,
                price=price,
                stock=stock,
                category_id=category_id,
                brand_id=brand_id,
                is_new=is_new,
                is_hot=is_hot,
                is_active=True
            )
            
            # Handle image upload (if exists)
            if 'image' in request.files:
                file = request.files['image']
                if file and file.filename:
                    from werkzeug.utils import secure_filename
                    import os
                    filename = secure_filename(file.filename)
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(filepath)
                    product.main_image = f'/static/uploads/{filename}'
            
            # Add to database and get ID
            db.session.add(product)
            db.session.flush()  # Important! Get product.id before commit
            
            # ✨ Handle variants
            variant_colors = request.form.getlist('variant_color[]')
            variant_editions = request.form.getlist('variant_edition[]')
            variant_prices = request.form.getlist('variant_price_modifier[]')
            variant_stocks = request.form.getlist('variant_stock[]')
            variant_skus = request.form.getlist('variant_sku[]')
            
            from models.product_variant import ProductVariant
            
            for i in range(len(variant_colors)):
                if not variant_colors[i] and not variant_editions[i]:
                    continue
                
                attributes = {}
                if variant_colors[i]:
                    attributes['color'] = variant_colors[i]
                if variant_editions[i]:
                    attributes['edition'] = variant_editions[i]
                
                variant = ProductVariant(
                    product_id=product.id,
                    sku=variant_skus[i] if i < len(variant_skus) and variant_skus[i] else None,
                    attributes=attributes,
                    price_modifier=float(variant_prices[i]) if i < len(variant_prices) and variant_prices[i] else 0.0,
                    stock=int(variant_stocks[i]) if i < len(variant_stocks) and variant_stocks[i] else 0,
                    is_active=True
                )
                db.session.add(variant)
            
            db.session.commit()
            flash('Product added successfully with variants!', 'success')
            return redirect(url_for('admin_products'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding product: {str(e)}', 'error')
            return redirect(url_for('admin_add_product'))
    
    # GET request
    from models.product import Category, Brand
    categories = Category.query.all()
    brands = Brand.query.all()
    return render_template('admin/add_product.html', 
                         categories=categories, 
                         brands=brands)


@app.route('/admin/product/<int:product_id>/edit', methods=['GET', 'POST'])
@login_required
def admin_edit_product(product_id):
    """Edit Product"""
    if not current_user.is_admin():
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('index'))
    
    from models.product import Product, Category, Brand
    
    product = Product.query.get_or_404(product_id)
    
    if request.method == 'POST':
        try:
            # Update basic information
            product.name = request.form.get('name')
            product.price = float(request.form.get('price'))
            product.stock = int(request.form.get('stock'))
            product.description = request.form.get('description', '')
            product.short_description = request.form.get('short_description', '')
            product.warranty_period = request.form.get('warranty_period', '')
            product.sku = request.form.get('sku', '')
            
            # Update category and brand
            category_id = request.form.get('category_id')
            brand_id = request.form.get('brand_id')
            product.category_id = int(category_id) if category_id else None
            product.brand_id = int(brand_id) if brand_id else None
            
            # Update original price
            original_price = request.form.get('original_price')
            if original_price:
                product.original_price = float(original_price)
            else:
                product.original_price = None
            
            # Update status checkboxes
            product.is_active = bool(request.form.get('is_active'))
            product.is_featured = bool(request.form.get('is_featured'))
            product.is_new = bool(request.form.get('is_new'))
            product.is_hot = bool(request.form.get('is_hot'))
            
            # Handle image uploads
            upload_folder = app.config['UPLOAD_FOLDER']
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)
            
            # Process main image
            if 'main_image' in request.files:
                file = request.files['main_image']
                if file and file.filename:
                    filename = secure_filename(file.filename)
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
                    filename = timestamp + filename
                    filepath = os.path.join(upload_folder, filename)
                    file.save(filepath)
                    product.main_image = f'/static/images/{filename}'
            
            # Process additional images
            for i in range(2, 5):
                field_name = f'image_{i}'
                if field_name in request.files:
                    file = request.files[field_name]
                    if file and file.filename:
                        filename = secure_filename(file.filename)
                        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
                        filename = timestamp + filename
                        filepath = os.path.join(upload_folder, filename)
                        file.save(filepath)
                        setattr(product, field_name, f'/static/images/{filename}')
            
            db.session.commit()

            # ---- Process new variants submitted via the form ----
            from models.product_variant import ProductVariant

            variant_colors   = request.form.getlist('variant_color[]')
            variant_editions = request.form.getlist('variant_edition[]')
            variant_prices   = request.form.getlist('variant_price_modifier[]')
            variant_stocks   = request.form.getlist('variant_stock[]')
            variant_skus     = request.form.getlist('variant_sku[]')

            for i in range(len(variant_colors)):
                color   = variant_colors[i]   if i < len(variant_colors)   else ''
                edition = variant_editions[i]  if i < len(variant_editions) else ''

                if not color and not edition:
                    continue  # Skip blank rows

                attributes = {}
                if color:
                    attributes['color'] = color
                if edition:
                    attributes['edition'] = edition

                price_mod = float(variant_prices[i]) if i < len(variant_prices) and variant_prices[i] else 0.0
                v_stock   = int(variant_stocks[i])   if i < len(variant_stocks)  and variant_stocks[i]  else 0
                v_sku     = variant_skus[i]           if i < len(variant_skus)   and variant_skus[i]    else None

                new_variant = ProductVariant(
                    product_id=product.id,
                    sku=v_sku,
                    attributes=attributes,
                    price_modifier=price_mod,
                    stock=v_stock,
                    is_active=True
                )
                db.session.add(new_variant)

            db.session.commit()

            flash(f'Product "{product.name}" updated successfully!', 'success')
            return redirect(url_for('admin_products'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error updating product: {str(e)}', 'error')
    
    # Get categories and brands for dropdown
    categories = Category.query.all()
    brands = Brand.query.all()
    
    return render_template('admin/edit_product.html', 
                         product=product,
                         categories=categories,
                         brands=brands)


@app.route('/admin/product/<int:product_id>/delete', methods=['POST'])
@login_required
def admin_delete_product(product_id):
    """Delete Product"""
    if not current_user.is_admin():
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('index'))
    
    from models.product import Product
    
    product = Product.query.get_or_404(product_id)
    product_name = product.name
    
    try:
        db.session.delete(product)
        db.session.commit()
        flash(f'Product "{product_name}" deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting product: {str(e)}', 'error')
    
    return redirect(url_for('admin_products'))



@app.route('/admin/variants/delete/<int:variant_id>', methods=['POST'])
@login_required
def admin_delete_variant(variant_id):
    """Delete a product variant"""
    from models.product_variant import ProductVariant
    
    try:
        variant = ProductVariant.query.get_or_404(variant_id)
        product_id = variant.product_id
        
        db.session.delete(variant)
        db.session.commit()
        flash('Variant deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting variant: {str(e)}', 'error')
    
    return redirect(url_for('admin_edit_product', product_id=product_id))


# ==================== WISHLIST ROUTES ====================

@app.route('/wishlist')
@login_required
def wishlist():
    """View user's wishlist"""
    from models.wishlist import Wishlist
    
    # Get all wishlist items for current user
    user_wishlist = Wishlist.query.filter_by(user_id=current_user.id).all()
    
    # Pass to template
    return render_template('wishlist.html', wishlist_items=user_wishlist)


@app.route('/wishlist/add/<int:product_id>', methods=['POST'])
@login_required
def add_to_wishlist(product_id):
    """Add product to wishlist"""
    from models.wishlist import Wishlist
    
    # Check if product exists
    product = Product.query.get_or_404(product_id)
    
    # Check if already in wishlist
    existing = Wishlist.query.filter_by(
        user_id=current_user.id,
        product_id=product_id
    ).first()
    
    if existing:
        flash('Product already in your wishlist!', 'info')
    else:
        # Add to wishlist
        new_item = Wishlist(
            user_id=current_user.id,
            product_id=product_id
        )
        db.session.add(new_item)
        db.session.commit()
        flash(f'"{product.name}" added to your wishlist!', 'success')
    
    # Redirect back
    return redirect(request.referrer or url_for('index'))


@app.route('/wishlist/remove/<int:product_id>', methods=['POST'])
@login_required
def remove_from_wishlist(product_id):
    """Remove product from wishlist"""
    from models.wishlist import Wishlist
    
    # Find wishlist item
    item = Wishlist.query.filter_by(
        user_id=current_user.id,
        product_id=product_id
    ).first_or_404()
    
    product_name = item.product.name
    
    # Delete from wishlist
    db.session.delete(item)
    db.session.commit()
    
    flash(f'"{product_name}" removed from wishlist!', 'success')
    return redirect(url_for('wishlist'))


# ==================== BUY NOW ROUTE ====================

# ==================== BUY NOW ROUTE ====================

@app.route('/buy-now/<int:product_id>', methods=['POST'])
@login_required
def buy_now(product_id):
    """Buy product immediately WITH VARIANT SUPPORT"""
    product = Product.query.get_or_404(product_id)
    quantity = request.form.get('quantity', 1, type=int)
    
    # ✨ NEW: Capture variant selection
    selected_color = request.form.get('color')
    selected_edition = request.form.get('edition')
    
    # Build variant attributes (Option A: independent modifiers)
    variant_attributes = {}
    if selected_color:
        variant_attributes['color'] = selected_color
    if selected_edition:
        variant_attributes['edition'] = selected_edition

    # Get or create cart
    cart = CartServiceFacade.get_or_create_cart(user_id=current_user.id)
    
    # Clear cart
    for item in cart.items:
        db.session.delete(item)
    db.session.commit()
    
    # Add selected product (no combined variant_id needed)
    success, message = CartServiceFacade.add_to_cart(
        cart,
        product_id,
        quantity,
        variant_id=None,
        variant_attributes=variant_attributes if variant_attributes else None
    )
    
    if not success:
        flash(message, 'error')
        return redirect(url_for('product_detail', slug=product.slug))
    
    # Redirect to checkout
    return redirect(url_for('checkout'))




# ==================== CHATBOT API ROUTE ====================

@app.route('/api/chatbot/message', methods=['POST'])
def chatbot_message():
    """
    Thin controller for the chatbot API.
    Delegates all logic to ChatbotFacade (services/chatbot_facade.py).
    This route is read-only; it never modifies cart, orders, or auth state.
    """
    from services.chatbot_facade import ChatbotFacade

    data = request.get_json(silent=True) or {}
    user_message = data.get('message', '').strip()[:500]   # hard cap at 500 chars

    response = ChatbotFacade.process(user_message)
    return jsonify(response)

# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found_error(error):
    """404 error handler"""
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    """500 error handler"""
    db.session.rollback()
    return render_template('500.html'), 500


# ==================== MAIN ====================

if __name__ == '__main__':
    with app.app_context():
        # Create all database tables
        db_manager.create_all(app)
        print("Database tables created!")
    
    # Run the application
    app.run(debug=True, host='0.0.0.0', port=5000)
