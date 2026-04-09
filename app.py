from flask import Flask, render_template, request, session, redirect, url_for, jsonify
import pyodbc
# NEW: Import security functions for password hashing
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
# This secret key protects the session cookies. 
app.secret_key = 'super_secret_project_key' 

def get_db_connection():
    conn = pyodbc.connect(
        'DRIVER={ODBC Driver 17 for SQL Server};'
        'SERVER=localhost;'  # <-- KEEP YOUR SERVER NAME HERE
        'DATABASE=EcommerceDB;'          
        'Trusted_Connection=yes;'        
    )
    return conn

# --- NEW ROUTE: The Landing Page ---
@app.route('/')
def landing_page():
    # Simply renders the new animated entrance screen
    return render_template('landing.html')

# --- MOVED ROUTE: The Actual Storefront ---
@app.route('/store')
def store():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Products')
    columns = [column[0] for column in cursor.description]
    products = [dict(zip(columns, row)) for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    
    cart_count = sum(session.get('cart', {}).values())
    
    # Notice we render index.html here, just like before
    return render_template('index.html', products=products, cart_count=cart_count)

# 2. Add to Cart Route (Now with AJAX support!)
@app.route('/add_to_cart/<int:product_id>')
def add_to_cart(product_id):
    cart = session.get('cart', {})
    pid = str(product_id)
    cart[pid] = cart.get(pid, 0) + 1
    session['cart'] = cart
    
    # Calculate the new total number of items
    new_cart_count = sum(cart.values())
    
    # Instead of redirecting, send back a success message and the new count
    return jsonify({'success': True, 'cart_count': new_cart_count})

# 3. View Cart Route
@app.route('/cart')
def view_cart():
    cart = session.get('cart', {})
    cart_items = []
    total_price = 0
    
    if cart:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Loop through the cart dictionary to fetch product details and calculate totals
        for pid, quantity in cart.items():
            cursor.execute('SELECT Title, Price, ImageURL FROM Products WHERE ProductID = ?', (pid,))
            row = cursor.fetchone()
            if row:
                item_total = float(row.Price) * quantity
                total_price += item_total
                cart_items.append({
                    'id': pid,
                    'title': row.Title,
                    'price': row.Price,
                    'image': row.ImageURL,
                    'quantity': quantity,
                    'total': round(item_total, 2)
                })
                
        cursor.close()
        conn.close()

    return render_template('cart.html', cart_items=cart_items, total_price=round(total_price, 2))

# 4. Clear Cart (Simulate Checkout)
@app.route('/checkout')
def checkout():
    # Empty the cart session
    session.pop('cart', None)
    return "<h2>Order Placed Successfully!</h2><a href='/'>Go back to store</a>"

# --- AUTHENTICATION ROUTES ---

# 5. Registration Route
@app.route('/register', methods=['GET', 'POST'])
def register(): 
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        
        # THE FLEX: Hash the password before saving it to the database
        hashed_pw = generate_password_hash(password)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Insert the new user into the database
            cursor.execute('INSERT INTO Users (FullName, Email, PasswordHash) VALUES (?, ?, ?)', (name, email, hashed_pw))
            conn.commit()
            return redirect(url_for('login'))
        except pyodbc.IntegrityError:
            # This triggers if the email already exists (because of our UNIQUE constraint in SQL)
            return "<h3>Error: Email already exists!</h3><a href='/register'>Try again</a>"
        finally:
            cursor.close()
            conn.close()
            
    return render_template('register.html')

# 6. Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Users WHERE Email = ?', (email,))
        
        # Format the row into a dictionary
        row = cursor.fetchone()
        if row:
            columns = [column[0] for column in cursor.description]
            user = dict(zip(columns, row))
            
            # THE FLEX: Verify the entered password against the hashed password
            if check_password_hash(user['PasswordHash'], password):
                session['user_id'] = user['UserID']
                session['user_name'] = user['FullName']
                return redirect(url_for('dashboard'))
        
        cursor.close()
        conn.close()
        return "<h3>Invalid email or password.</h3><a href='/login'>Try again</a>"
        
    return render_template('login.html')

# 7. Dashboard Route (Protected!)
@app.route('/dashboard')
def dashboard():
    # Route Protection: If they aren't logged in, kick them to the login page
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    return render_template('dashboard.html', name=session['user_name'])

# 8. Logout Route
@app.route('/logout')
def logout():
    # Remove user data from the session
    session.pop('user_id', None)
    session.pop('user_name', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)