from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
import sys
from functools import wraps

# Fix import path
current_dir = os.path.dirname(os.path.abspath(__file__))
models_dir = os.path.join(current_dir, 'models')
sys.path.insert(0, models_dir)

from db import *

app = Flask(__name__)
app.secret_key = 'ezgadgets-secret-key-change-in-production-2024'

# Initialize database
with app.app_context():
    db_dir = os.path.join(current_dir, 'database')
    os.makedirs(db_dir, exist_ok=True)
    init_database()

# Decorators
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this page', 'error')
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this page', 'error')
            return redirect(url_for('login'))
        user = get_user_by_id(session['user_id'])
        if not user or user['role'] != 'admin':
            flash('Access denied. Admin privileges required.', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

# Helper functions
def get_cart_total():
    cart = session.get('cart', {})
    total_price = 0
    total_items = 0
    
    for product_id, quantity in cart.items():
        product = get_product_by_id(int(product_id))
        if product:
            total_price += product['price'] * quantity
            total_items += quantity
    
    return {'total_price': round(total_price, 2), 'total_items': total_items}

def get_cart_items():
    cart = session.get('cart', {})
    cart_items = []
    
    for product_id, quantity in cart.items():
        product = get_product_by_id(int(product_id))
        if product:
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'subtotal': round(product['price'] * quantity, 2)
            })
    
    return cart_items

# Context processor
@app.context_processor
def inject_global_data():
    cart_total = get_cart_total()
    categories = get_categories()
    user = None
    if 'user_id' in session:
        user = get_user_by_id(session['user_id'])
    return dict(cart_total=cart_total, all_categories=categories, current_user=user)

# Authentication routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = authenticate_user(email, password)
        if user:
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            session['user_role'] = user['role']
            flash(f'Welcome back, {user["name"]}!', 'success')
            
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('admin_dashboard') if user['role'] == 'admin' else url_for('account'))
        else:
            flash('Invalid email or password', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        name = request.form.get('name')
        phone = request.form.get('phone', '')
        
        if password != confirm_password:
            flash('Passwords do not match', 'error')
        elif len(password) < 6:
            flash('Password must be at least 6 characters', 'error')
        else:
            user_id = create_user(email, password, name, phone)
            if user_id:
                flash('Account created successfully! Please login.', 'success')
                return redirect(url_for('login'))
            else:
                flash('Email already exists', 'error')
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'success')
    return redirect(url_for('index'))

# User account routes
@app.route('/account')
@login_required
def account():
    user = get_user_by_id(session['user_id'])
    orders = get_user_orders(session['user_id'])
    return render_template('account.html', user=user, orders=orders)

@app.route('/account/update', methods=['POST'])
@login_required
def update_account():
    name = request.form.get('name')
    phone = request.form.get('phone')
    address = request.form.get('address')
    
    if update_user_profile(session['user_id'], name, phone, address):
        session['user_name'] = name
        flash('Profile updated successfully', 'success')
    else:
        flash('Error updating profile', 'error')
    
    return redirect(url_for('account'))

@app.route('/order/<int:order_id>')
@login_required
def view_order(order_id):
    order = get_order_by_id(order_id)
    if not order or (order['user_id'] != session['user_id'] and session.get('user_role') != 'admin'):
        flash('Order not found', 'error')
        return redirect(url_for('account'))
    
    items = get_order_items(order_id)
    return render_template('order_detail.html', order=order, items=items)

# Main routes
@app.route('/')
def index():
    featured_products = get_featured_products(8)
    categories = get_categories()
    return render_template('index.html', featured_products=featured_products, categories=categories)

@app.route('/products')
def products():
    category = request.args.get('category')
    search_query = request.args.get('q')
    
    if search_query:
        products_list = search_products(search_query)
    elif category:
        products_list = get_products_by_category(category)
    else:
        products_list = get_all_products()
    
    categories = get_categories()
    return render_template('products.html', products=products_list, categories=categories, 
                         selected_category=category, search_query=search_query)

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    product = get_product_by_id(product_id)
    if not product:
        flash('Product not found', 'error')
        return redirect(url_for('products'))
    
    specs = get_product_specs(product_id)
    return render_template('product.html', product=product, specs=specs)

# Cart routes
@app.route('/cart')
def cart():
    cart_items = get_cart_items()
    cart_total = get_cart_total()
    return render_template('cart.html', cart_items=cart_items, cart_total=cart_total)

@app.route('/add-to-cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    product = get_product_by_id(product_id)
    if not product:
        flash('Product not found', 'error')
        return redirect(url_for('products'))
    
    quantity = int(request.form.get('quantity', 1))
    
    if 'cart' not in session:
        session['cart'] = {}
    
    cart = session['cart']
    product_id_str = str(product_id)
    current_quantity = cart.get(product_id_str, 0)
    new_quantity = current_quantity + quantity
    
    if not check_stock(product_id, new_quantity):
        flash(f'Sorry, only {product["stock"]} units available', 'error')
        return redirect(request.referrer or url_for('products'))
    
    cart[product_id_str] = new_quantity
    session['cart'] = cart
    session.modified = True
    
    flash(f'{product["name"]} added to cart', 'success')
    return redirect(request.referrer or url_for('products'))

@app.route('/update-cart/<int:product_id>', methods=['POST'])
def update_cart(product_id):
    quantity = int(request.form.get('quantity', 1))
    
    if quantity < 1:
        return redirect(url_for('remove_from_cart', product_id=product_id))
    
    if not check_stock(product_id, quantity):
        product = get_product_by_id(product_id)
        flash(f'Sorry, only {product["stock"]} units available', 'error')
        return redirect(url_for('cart'))
    
    cart = session.get('cart', {})
    cart[str(product_id)] = quantity
    session['cart'] = cart
    session.modified = True
    flash('Cart updated', 'success')
    return redirect(url_for('cart'))

@app.route('/remove-from-cart/<int:product_id>')
def remove_from_cart(product_id):
    cart = session.get('cart', {})
    if str(product_id) in cart:
        del cart[str(product_id)]
        session['cart'] = cart
        session.modified = True
        flash('Item removed from cart', 'success')
    return redirect(url_for('cart'))

@app.route('/clear-cart')
def clear_cart():
    session['cart'] = {}
    session.modified = True
    flash('Cart cleared', 'success')
    return redirect(url_for('cart'))

# Checkout routes
@app.route('/checkout')
def checkout():
    cart_items = get_cart_items()
    if not cart_items:
        flash('Your cart is empty', 'error')
        return redirect(url_for('products'))
    
    cart_total = get_cart_total()
    user = None
    if 'user_id' in session:
        user = get_user_by_id(session['user_id'])
    
    return render_template('checkout.html', cart_items=cart_items, cart_total=cart_total, user=user)

@app.route('/place-order', methods=['POST'])
def place_order():
    cart_items = get_cart_items()
    if not cart_items:
        flash('Your cart is empty', 'error')
        return redirect(url_for('products'))
    
    name = request.form.get('name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    address = request.form.get('address')
    payment_method = request.form.get('payment', 'cod')
    notes = request.form.get('notes', '')
    
    if not all([name, email, phone, address]):
        flash('Please fill in all required fields', 'error')
        return redirect(url_for('checkout'))
    
    cart_total = get_cart_total()
    user_id = session.get('user_id')
    
    # Create order
    order_id = create_order(user_id, name, email, phone, address, 
                           cart_total['total_price'], payment_method, notes)
    
    # Add order items and update stock
    for item in cart_items:
        add_order_item(order_id, item['product']['id'], item['product']['name'],
                      item['quantity'], item['product']['price'])
        update_stock(item['product']['id'], -item['quantity'])
    
    # Clear cart
    session['cart'] = {}
    session.modified = True
    
    flash(f'Thank you {name}! Your order #{order_id} has been placed successfully.', 'success')
    
    if user_id:
        return redirect(url_for('view_order', order_id=order_id))
    return redirect(url_for('index'))

# Admin routes
@app.route('/admin')
@admin_required
def admin_dashboard():
    total_orders = len(get_all_orders())
    total_products = len(get_all_products())
    pending_orders = len([o for o in get_all_orders() if o['status'] == 'pending'])
    
    recent_orders = get_all_orders()[:10]
    
    return render_template('admin/dashboard.html', 
                         total_orders=total_orders,
                         total_products=total_products,
                         pending_orders=pending_orders,
                         recent_orders=recent_orders)

@app.route('/admin/orders')
@admin_required
def admin_orders():
    orders = get_all_orders()
    return render_template('admin/orders.html', orders=orders)

@app.route('/admin/order/<int:order_id>')
@admin_required
def admin_order_detail(order_id):
    order = get_order_by_id(order_id)
    if not order:
        flash('Order not found', 'error')
        return redirect(url_for('admin_orders'))
    
    items = get_order_items(order_id)
    return render_template('admin/order_detail.html', order=order, items=items)

@app.route('/admin/order/<int:order_id>/update-status', methods=['POST'])
@admin_required
def admin_update_order_status(order_id):
    status = request.form.get('status')
    if update_order_status(order_id, status):
        flash('Order status updated', 'success')
    else:
        flash('Error updating order status', 'error')
    return redirect(url_for('admin_order_detail', order_id=order_id))

@app.route('/admin/products')
@admin_required
def admin_products():
    products = get_all_products()
    return render_template('admin/products.html', products=products)

@app.route('/admin/product/add', methods=['GET', 'POST'])
@admin_required
def admin_add_product():
    if request.method == 'POST':
        name = request.form.get('name')
        category = request.form.get('category')
        price = float(request.form.get('price'))
        stock = int(request.form.get('stock'))
        image = request.form.get('image', 'product.jpg')
        description = request.form.get('description')
        
        product_id = add_product(name, category, price, stock, image, description)
        flash('Product added successfully', 'success')
        return redirect(url_for('admin_products'))
    
    categories = get_categories()
    return render_template('admin/product_form.html', categories=categories)

@app.route('/admin/product/<int:product_id>/edit', methods=['GET', 'POST'])
@admin_required
def admin_edit_product(product_id):
    product = get_product_by_id(product_id)
    if not product:
        flash('Product not found', 'error')
        return redirect(url_for('admin_products'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        category = request.form.get('category')
        price = float(request.form.get('price'))
        stock = int(request.form.get('stock'))
        image = request.form.get('image')
        description = request.form.get('description')
        
        update_product(product_id, name, category, price, stock, image, description)
        flash('Product updated successfully', 'success')
        return redirect(url_for('admin_products'))
    
    categories = get_categories()
    return render_template('admin/product_form.html', product=product, categories=categories)

@app.route('/admin/product/<int:product_id>/delete', methods=['POST'])
@admin_required
def admin_delete_product(product_id):
    if delete_product(product_id):
        flash('Product deleted successfully', 'success')
    else:
        flash('Error deleting product', 'error')
    return redirect(url_for('admin_products'))

# Static pages
@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)