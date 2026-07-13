from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
import mysql.connector
from functools import wraps
import json

app = Flask(__name__)
app.secret_key = 'food_ordering_secret_key_2024'

# ─────────────────────────────────────────
# DB CONFIG — update with your credentials
# ─────────────────────────────────────────
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'roghani00.',   # ← Change this
    'database': 'food_ordering_db'
}

def get_db():
    return mysql.connector.connect(**DB_CONFIG)

# ─────────────────────────────────────────
# Auth Decorators
# ─────────────────────────────────────────
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'customer_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'admin_id' not in session:
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated

# ─────────────────────────────────────────
# CUSTOMER ROUTES
# ─────────────────────────────────────────

@app.route('/')
def index():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM categories")
    categories = cursor.fetchall()
    cursor.execute("SELECT m.*, c.name as category_name FROM menu_items m JOIN categories c ON m.category_id = c.id WHERE m.is_available = TRUE LIMIT 6")
    featured = cursor.fetchall()
    db.close()
    return render_template('index.html', categories=categories, featured=featured)

@app.route('/menu')
def menu():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM categories")
    categories = cursor.fetchall()
    cat_id = request.args.get('category', None)
    if cat_id:
        cursor.execute("SELECT m.*, c.name as cat_name FROM menu_items m JOIN categories c ON m.category_id = c.id WHERE m.is_available = TRUE AND m.category_id = %s", (cat_id,))
    else:
        cursor.execute("SELECT m.*, c.name as cat_name FROM menu_items m JOIN categories c ON m.category_id = c.id WHERE m.is_available = TRUE")
    items = cursor.fetchall()
    db.close()
    return render_template('menu.html', categories=categories, items=items, selected_cat=cat_id)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        phone = request.form['phone']
        address = request.form['address']
        db = get_db()
        cursor = db.cursor()
        try:
            cursor.execute("INSERT INTO customers (name, email, password, phone, address) VALUES (%s,%s,%s,%s,%s)",
                           (name, email, password, phone, address))
            db.commit()
            flash('Account created! Please login.', 'success')
            return redirect(url_for('login'))
        except mysql.connector.IntegrityError:
            flash('Email already registered.', 'error')
        finally:
            db.close()
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM customers WHERE email=%s AND password=%s", (email, password))
        customer = cursor.fetchone()
        db.close()
        if customer:
            session['customer_id'] = customer['id']
            session['customer_name'] = customer['name']
            return redirect(url_for('index'))
        flash('Invalid credentials.', 'error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('customer_id', None)
    session.pop('customer_name', None)
    return redirect(url_for('index'))

@app.route('/cart')
@login_required
def cart():
    return render_template('cart.html')

@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    if request.method == 'POST':
        cart_data = request.form.get('cart_data')
        delivery_address = request.form.get('delivery_address')
        payment_method = request.form.get('payment_method')
        cart_items = json.loads(cart_data)

        db = get_db()
        cursor = db.cursor(dictionary=True)

        # Calculate total
        total = sum(item['price'] * item['qty'] for item in cart_items)

        # Insert order
        cursor.execute("""
            INSERT INTO orders (customer_id, total_amount, delivery_address, payment_method, payment_status)
            VALUES (%s, %s, %s, %s, 'paid')
        """, (session['customer_id'], total, delivery_address, payment_method))
        order_id = cursor.lastrowid

        # Insert order items
        for item in cart_items:
            cursor.execute("""
                INSERT INTO order_items (order_id, menu_item_id, quantity, unit_price)
                VALUES (%s, %s, %s, %s)
            """, (order_id, item['id'], item['qty'], item['price']))

        db.commit()
        db.close()
        return redirect(url_for('order_success', order_id=order_id))

    # GET: load customer info
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM customers WHERE id=%s", (session['customer_id'],))
    customer = cursor.fetchone()
    db.close()
    return render_template('checkout.html', customer=customer)

@app.route('/order-success/<int:order_id>')
@login_required
def order_success(order_id):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM orders WHERE id=%s AND customer_id=%s", (order_id, session['customer_id']))
    order = cursor.fetchone()
    db.close()
    return render_template('order_success.html', order=order)

@app.route('/my-orders')
@login_required
def my_orders():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT o.*, 
               GROUP_CONCAT(CONCAT(oi.quantity,'x ', m.name) SEPARATOR ', ') as items_summary
        FROM orders o
        JOIN order_items oi ON oi.order_id = o.id
        JOIN menu_items m ON m.id = oi.menu_item_id
        WHERE o.customer_id = %s
        GROUP BY o.id
        ORDER BY o.created_at DESC
    """, (session['customer_id'],))
    orders = cursor.fetchall()
    db.close()
    return render_template('my_orders.html', orders=orders)

@app.route('/track-order/<int:order_id>')
@login_required
def track_order(order_id):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM orders WHERE id=%s AND customer_id=%s", (order_id, session['customer_id']))
    order = cursor.fetchone()
    cursor.execute("""
        SELECT oi.*, m.name, m.price FROM order_items oi
        JOIN menu_items m ON m.id = oi.menu_item_id
        WHERE oi.order_id = %s
    """, (order_id,))
    items = cursor.fetchall()
    db.close()
    return render_template('track_order.html', order=order, items=items)

# ─────────────────────────────────────────
# ADMIN ROUTES
# ─────────────────────────────────────────

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM admins WHERE username=%s AND password=%s", (username, password))
        admin = cursor.fetchone()
        db.close()
        if admin:
            session['admin_id'] = admin['id']
            session['admin_name'] = admin['username']
            return redirect(url_for('admin_dashboard'))
        flash('Invalid admin credentials.', 'error')
    return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_id', None)
    session.pop('admin_name', None)
    return redirect(url_for('admin_login'))

@app.route('/admin')
@admin_required
def admin_dashboard():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT COUNT(*) as cnt FROM orders")
    total_orders = cursor.fetchone()['cnt']
    cursor.execute("SELECT COUNT(*) as cnt FROM orders WHERE status='pending'")
    pending_orders = cursor.fetchone()['cnt']
    cursor.execute("SELECT SUM(total_amount) as total FROM orders WHERE payment_status='paid'")
    revenue = cursor.fetchone()['total'] or 0
    cursor.execute("SELECT COUNT(*) as cnt FROM customers")
    total_customers = cursor.fetchone()['cnt']
    cursor.execute("""
        SELECT o.*, c.name as customer_name FROM orders o
        JOIN customers c ON c.id = o.customer_id
        ORDER BY o.created_at DESC LIMIT 8
    """)
    recent_orders = cursor.fetchall()
    db.close()
    return render_template('admin_dashboard.html',
        total_orders=total_orders,
        pending_orders=pending_orders,
        revenue=revenue,
        total_customers=total_customers,
        recent_orders=recent_orders
    )

@app.route('/admin/orders')
@admin_required
def admin_orders():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    status_filter = request.args.get('status', '')
    if status_filter:
        cursor.execute("""
            SELECT o.*, c.name as customer_name, c.phone
            FROM orders o JOIN customers c ON c.id=o.customer_id
            WHERE o.status=%s ORDER BY o.created_at DESC
        """, (status_filter,))
    else:
        cursor.execute("""
            SELECT o.*, c.name as customer_name, c.phone
            FROM orders o JOIN customers c ON c.id=o.customer_id
            ORDER BY o.created_at DESC
        """)
    orders = cursor.fetchall()
    db.close()
    return render_template('admin_orders.html', orders=orders, status_filter=status_filter)

@app.route('/admin/order/<int:order_id>')
@admin_required
def admin_order_detail(order_id):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT o.*, c.name as customer_name, c.email, c.phone
        FROM orders o JOIN customers c ON c.id=o.customer_id
        WHERE o.id=%s
    """, (order_id,))
    order = cursor.fetchone()
    cursor.execute("""
        SELECT oi.*, m.name FROM order_items oi
        JOIN menu_items m ON m.id=oi.menu_item_id
        WHERE oi.order_id=%s
    """, (order_id,))
    items = cursor.fetchall()
    db.close()
    return render_template('admin_order_detail.html', order=order, items=items)

@app.route('/admin/order/update-status', methods=['POST'])
@admin_required
def update_order_status():
    order_id = request.form['order_id']
    status = request.form['status']
    db = get_db()
    cursor = db.cursor()
    cursor.execute("UPDATE orders SET status=%s WHERE id=%s", (status, order_id))
    db.commit()
    db.close()
    return redirect(url_for('admin_order_detail', order_id=order_id))

@app.route('/admin/menu')
@admin_required
def admin_menu():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT m.*, c.name as cat_name FROM menu_items m
        JOIN categories c ON c.id=m.category_id
        ORDER BY c.id, m.name
    """)
    items = cursor.fetchall()
    cursor.execute("SELECT * FROM categories")
    categories = cursor.fetchall()
    db.close()
    return render_template('admin_menu.html', items=items, categories=categories)

@app.route('/admin/menu/add', methods=['POST'])
@admin_required
def admin_add_item():
    name = request.form['name']
    description = request.form['description']
    price = request.form['price']
    category_id = request.form['category_id']
    db = get_db()
    cursor = db.cursor()
    cursor.execute("INSERT INTO menu_items (name, description, price, category_id) VALUES (%s,%s,%s,%s)",
                   (name, description, price, category_id))
    db.commit()
    db.close()
    flash('Item added successfully!', 'success')
    return redirect(url_for('admin_menu'))

@app.route('/admin/menu/toggle/<int:item_id>')
@admin_required
def toggle_item(item_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("UPDATE menu_items SET is_available = NOT is_available WHERE id=%s", (item_id,))
    db.commit()
    db.close()
    return redirect(url_for('admin_menu'))

@app.route('/admin/menu/delete/<int:item_id>')
@admin_required
def delete_item(item_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM menu_items WHERE id=%s", (item_id,))
    db.commit()
    db.close()
    return redirect(url_for('admin_menu'))

@app.route('/admin/customers')
@admin_required
def admin_customers():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT c.*, COUNT(o.id) as order_count
        FROM customers c LEFT JOIN orders o ON o.customer_id=c.id
        GROUP BY c.id ORDER BY c.created_at DESC
    """)
    customers = cursor.fetchall()
    db.close()
    return render_template('admin_customers.html', customers=customers)

if __name__ == '__main__':
    app.run(debug=True)
