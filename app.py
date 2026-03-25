from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'farmconnect_ultra_final'

# ------------------ DATABASE ------------------
def init_db():
    conn = sqlite3.connect("farmers.db")
    cursor = conn.cursor()
    # Users Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_type TEXT, name TEXT, country TEXT, 
        state TEXT, district TEXT, phone TEXT, aadhar TEXT, password TEXT
    )
    """)
    # Crops Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS crops(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        farmer_name TEXT, crop_name TEXT, quantity TEXT, price REAL, location TEXT
    )
    """)
    # NEW: Market Prices Table for Startup Logic
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS market_prices(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        state TEXT, district TEXT, market_name TEXT,
        commodity TEXT, modal_price REAL, arrival_date TEXT
    )
    """)
    conn.commit()
    conn.close()

init_db()

# ------------------ ROUTES ------------------

@app.route("/")
def home():
    try:
        conn = sqlite3.connect("farmers.db")
        cursor = conn.cursor()
        f_count = cursor.execute("SELECT COUNT(*) FROM users WHERE user_type='farmer'").fetchone()[0]
        b_count = cursor.execute("SELECT COUNT(*) FROM users WHERE user_type='buyer'").fetchone()[0]
        p_count = cursor.execute("SELECT COUNT(*) FROM crops").fetchone()[0]
        conn.close()
    except:
        f_count, b_count, p_count = 0, 0, 0
    return render_template("index.html", counts={"farmers": f_count, "buyers": b_count, "products": p_count, "countries": 1})

# NEW: Insights Page Logic
@app.route("/insights")
def insights():
    conn = sqlite3.connect("farmers.db")
    cursor = conn.cursor()
    # Fetching real price data (for now we show a list, later we use Plotly)
    market_data = cursor.execute("SELECT commodity, modal_price, district, market_name FROM market_prices ORDER BY modal_price DESC").fetchall()
    conn.close()
    return render_template("insights.html", market_data=market_data)

@app.route("/register")
def register_page():
    return render_template("registration.html")

@app.route("/post_register", methods=["POST"])
def post_register():
    u_type = request.form.get('user_type', 'farmer')
    u_name = request.form.get('name', 'User')
    data = (u_type, u_name, request.form.get('country', 'India'), request.form.get('state', ''), 
            request.form.get('district', ''), request.form.get('phone', ''), 
            request.form.get('aadhar', ''), request.form.get('password', ''))
    conn = sqlite3.connect("farmers.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (user_type, name, country, state, district, phone, aadhar, password) VALUES (?,?,?,?,?,?,?,?)", data)
    conn.commit()
    conn.close()
    session['user_name'] = u_name
    return redirect(url_for('sell_page' if u_type == 'farmer' else 'marketplace_page'))

@app.route("/login")
def login_page():
    return render_template("login.html")

@app.route("/post_login", methods=["POST"])
def post_login():
    name = request.form.get('name')
    password = request.form.get('password')
    conn = sqlite3.connect("farmers.db")
    cursor = conn.cursor()
    user = cursor.execute("SELECT * FROM users WHERE name=? AND password=?", (name, password)).fetchone()
    conn.close()
    if user:
        session['user_name'] = user[2]
        return redirect(url_for('sell_page' if user[1] == 'farmer' else 'marketplace_page'))
    return "Invalid Details. <a href='/login'>Try Again</a>"

@app.route("/sell")
def sell_page():
    return render_template("sell.html")

@app.route("/post_sell", methods=["POST"])
def post_sell():
    data = (session.get('user_name', 'Guest'), request.form.get('crop_name'), 
            request.form.get('quantity'), request.form.get('price'), request.form.get('location'))
    conn = sqlite3.connect("farmers.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO crops (farmer_name, crop_name, quantity, price, location) VALUES (?,?,?,?,?)", data)
    conn.commit()
    conn.close()
    return redirect(url_for('marketplace_page'))

@app.route("/marketplace")
def marketplace_page():
    conn = sqlite3.connect("farmers.db")
    cursor = conn.cursor()
    all_crops = cursor.execute("SELECT * FROM crops ORDER BY id DESC").fetchall()
    conn.close()
    return render_template("marketplace.html", crops=all_crops)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(debug=True)