from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'farmconnect_ultra_final'
UPLOAD_FOLDER = 'static/uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def get_db_connection():
    conn = sqlite3.connect("farmers.db")
    conn.row_factory = sqlite3.Row  # This allows accessing columns by name
    return conn

def init_db():
    conn = sqlite3.connect("farmers.db")
    cursor = conn.cursor()
    # UPDATED SCHEMA
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_type TEXT, name TEXT, country TEXT,
        state TEXT, district TEXT, phone TEXT, aadhar TEXT, password TEXT,
        truck_model TEXT, capacity TEXT, experience TEXT
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS crops(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        farmer_name TEXT, crop_name TEXT, quantity TEXT,
        price REAL, location TEXT, crop_type TEXT,
        harvest_date TEXT, image_url TEXT, video_url TEXT
    )
    """)
    conn.commit()
    conn.close()

init_db()

@app.route("/")
def home():
    conn = get_db_connection()
    f_count = conn.execute("SELECT COUNT(*) FROM users WHERE user_type='farmer'").fetchone()[0]
    b_count = conn.execute("SELECT COUNT(*) FROM users WHERE user_type='buyer'").fetchone()[0]
    p_count = conn.execute("SELECT COUNT(*) FROM crops").fetchone()[0]
    c_count = conn.execute("SELECT COUNT(DISTINCT state) FROM users").fetchone()[0]
    conn.close()
    return render_template("index.html", counts={
        "farmers": f_count or 0,
        "buyers": b_count or 0,
        "products": p_count or 0,
        "countries": c_count or 1
    })

# --- DASHBOARD REDIRECT ---
@app.route("/dashboard")
def dashboard():
    # This points to your live officially deployed Streamlit link
    live_dashboard_url = "https://farmconnect-dashboard-gmdiag4bzhje38myes2xmb.streamlit.app/"
    return redirect(live_dashboard_url)

@app.route("/register")
def register():
    return render_template("registration.html")

@app.route("/post_register", methods=["POST"])
def post_register():
    data = request.form
    u_type = data.get('user_type')
    conn = get_db_connection()
    conn.execute("""
        INSERT INTO users (user_type, name, country, state, district, phone, aadhar, password, truck_model, capacity, experience)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        u_type, data.get('name'), data.get('country'), data.get('state'), 
        data.get('district'), data.get('phone'), data.get('aadhar'), data.get('password'),
        data.get('truck_model'), data.get('capacity'), data.get('experience')
    ))
    conn.commit()
    conn.close()
    session['user_name'] = data.get('name')
    session['user_type'] = u_type
    
    if u_type == 'farmer':
        return redirect(url_for('sell_page'))
    elif u_type == 'delivery':
        return redirect(url_for('delivery_dashboard'))
    else:
        return redirect(url_for('marketplace_page'))

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/post_login", methods=["POST"])
def post_login():
    name = request.form.get('name')
    pwd = request.form.get('password')
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE name=? AND password=?", (name, pwd)).fetchone()
    conn.close()
    if user:
        session['user_name'] = user['name']
        session['user_type'] = user['user_type']
        if user['user_type'] == 'farmer':
            return redirect(url_for('sell_page'))
        elif user['user_type'] == 'delivery':
            return redirect(url_for('delivery_dashboard'))
        else:
            return redirect(url_for('marketplace_page'))
    return "Invalid Details. <a href='/login'>Try Again</a>"

@app.route("/delivery_dashboard")
def delivery_dashboard():
    if 'user_name' not in session or session.get('user_type') != 'delivery':
        return redirect(url_for('login'))
    return render_template("delivery.html")

@app.route("/marketplace")
def marketplace_page():
    conn = get_db_connection()
    crops = conn.execute("SELECT * FROM crops").fetchall()
    conn.close()
    return render_template("marketplace.html", crops=crops)

@app.route("/crop_details/<int:crop_id>")
def crop_details(crop_id):
    conn = get_db_connection()
    crop = conn.execute("SELECT * FROM crops WHERE id=?", (crop_id,)).fetchone()
    conn.close()
    if crop:
        return render_template("crop_details.html", crop=crop)
    return "Crop not found", 404

@app.route("/connect_with_farmer/<int:crop_id>")
def connect_with_farmer(crop_id):
    if 'user_name' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    crop = conn.execute("SELECT * FROM crops WHERE id=?", (crop_id,)).fetchone()
    farmer = conn.execute("SELECT * FROM users WHERE name=? AND user_type='farmer'", (crop['farmer_name'],)).fetchone()
    
    if not farmer:
        conn.close()
        return "Farmer details not found."

    delivery_partner = conn.execute(
        "SELECT * FROM users WHERE user_type='delivery' AND district=? LIMIT 1", 
        (farmer['district'],)
    ).fetchone()
    
    conn.close()

    buyer_msg = f"Hi {farmer['name']}, I want to buy your {crop['crop_name']}. Let's confirm!"
    farmer_link = f"https://wa.me/{farmer['phone']}?text={buyer_msg.replace(' ', '%20')}"

    driver_link = None
    if delivery_partner:
        loc_link = f"https://www.google.com/maps/search/?api=1&query={farmer['district']}+{farmer['state']}"
        driver_msg = f"New Delivery! Pick up {crop['crop_name']} from {farmer['name']} in {farmer['district']}. Location: {loc_link}"
        driver_link = f"https://wa.me/{delivery_partner['phone']}?text={driver_msg.replace(' ', '%20')}"

    return render_template("delivery.html", 
                           farmer_link=farmer_link, 
                           driver_link=driver_link, 
                           partner=delivery_partner,
                           farmer=farmer,
                           crop=crop)

@app.route("/sell")
def sell_page():
    if 'user_name' not in session:
        return redirect(url_for('login'))
    return render_template("sell.html")

@app.route("/post_sell", methods=["POST"])
def post_sell():
    if 'user_name' not in session:
        return redirect(url_for('login'))
    img = request.files.get('crop_image')
    vid = request.files.get('crop_video')
    img_fn = "default.jpg"
    if img and img.filename != "":
        img_fn = secure_filename(img.filename)
        img.save(os.path.join(app.config['UPLOAD_FOLDER'], img_fn))
    vid_fn = ""
    if vid and vid.filename != "":
        vid_fn = secure_filename(vid.filename)
        vid.save(os.path.join(app.config['UPLOAD_FOLDER'], vid_fn))
    
    conn = get_db_connection()
    conn.execute("""
    INSERT INTO crops (farmer_name, crop_name, quantity, price, location, crop_type, harvest_date, image_url, video_url)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        session['user_name'], request.form.get('crop_name'), request.form.get('quantity'),
        request.form.get('price'), request.form.get('location'), request.form.get('crop_type'),
        request.form.get('harvest_date'), img_fn, vid_fn
    ))
    conn.commit()
    conn.close()
    return redirect(url_for('marketplace_page'))

if __name__ == "__main__":
    app.run(debug=True)