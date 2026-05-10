from flask import Flask, render_template, request, session, redirect, url_for, jsonify
import pyodbc

from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

app.secret_key = 'super_secret_project_key' 

def get_db_connection():
    conn = pyodbc.connect(
        'DRIVER={ODBC Driver 17 for SQL Server};'
        'SERVER=localhost;' 
        'DATABASE=EcommerceDB;'          
        'Trusted_Connection=yes;'        
    )
    return conn


@app.route('/')
def landing_page():
    return render_template('landing.html')

@app.route('/store')
def store():
    search_query = request.args.get('q', '')
    category_filter = request.args.get('category', '')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    

    cursor.execute('SELECT DISTINCT Category FROM Products WHERE Category IS NOT NULL')
    categories = [row[0] for row in cursor.fetchall()]
    
    query = 'SELECT * FROM Products WHERE 1=1'
    params = []
    
    if search_query:
        query += ' AND (Title LIKE ? OR Description LIKE ?)'
        search_term = f'%{search_query}%'
        params.extend([search_term, search_term])
        
    if category_filter:
        query += ' AND Category = ?'
        params.append(category_filter)
        
    cursor.execute(query, params)
        
    columns = [column[0] for column in cursor.description]
    products = [dict(zip(columns, row)) for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    
    cart_count = sum(session.get('cart', {}).values())
    
    return render_template('index.html', products=products, cart_count=cart_count, search_query=search_query, categories=categories, current_category=category_filter)

# 2. Add to Cart Route 
@app.route('/add_to_cart/<int:product_id>')
def add_to_cart(product_id):
    cart = session.get('cart', {})
    pid = str(product_id)
    cart[pid] = cart.get(pid, 0) + 1
    session['cart'] = cart
    
    new_cart_count = sum(cart.values())
    
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

# 4. Clear Cart 
@app.route('/clear_cart')
def clear_cart():
    session.pop('cart', None)
    return redirect(url_for('view_cart'))

@app.route('/checkout')
def checkout():
   
    if 'user_id' not in session:
        return redirect(url_for('login', next=request.path))
        

    session.pop('cart', None)
    return render_template('success.html')
# --- AUTHENTICATION ROUTES ---

# 5. Registration Route
@app.route('/register', methods=['GET', 'POST'])
def register(): 
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        

        hashed_pw = generate_password_hash(password)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
           
            cursor.execute('INSERT INTO Users (FullName, Email, PasswordHash) VALUES (?, ?, ?)', (name, email, hashed_pw))
            conn.commit()
            return redirect(url_for('login'))
        except pyodbc.IntegrityError:
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
        next_url = request.form.get('next')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Users WHERE Email = ?', (email,))
        

        row = cursor.fetchone()
        if row:
            columns = [column[0] for column in cursor.description]
            user = dict(zip(columns, row))
            
  
            if check_password_hash(user['PasswordHash'], password):
                session['user_id'] = user['UserID']
                session['user_name'] = user['FullName']
                cursor.close()
                conn.close()
                if next_url:
                    return redirect(next_url)
                return redirect(url_for('dashboard'))
        
        cursor.close()
        conn.close()
        return "<h3>Invalid email or password.</h3><a href='/login'>Try again</a>"
        
    return render_template('login.html', next=request.args.get('next'))

# 7. Dashboard Route (Protected!)
@app.route('/dashboard')
def dashboard():

    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    return render_template('dashboard.html', name=session['user_name'])

# 8. Logout Route

@app.route('/logout')
def logout():

    session.pop('user_id', None)
    session.pop('user_name', None)
    
  
    return redirect(url_for('landing_page'))

if __name__ == '__main__':
    app.run(debug=True)
