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

def init_db():
    conn = sqlite3.connect("farmers.db")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_type TEXT, name TEXT, country TEXT,
        state TEXT, district TEXT, phone TEXT, aadhar TEXT, password TEXT
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
    conn = sqlite3.connect("farmers.db")
    cursor = conn.cursor()
    f_count = cursor.execute("SELECT COUNT(*) FROM users WHERE user_type='farmer'").fetchone()[0]
    b_count = cursor.execute("SELECT COUNT(*) FROM users WHERE user_type='buyer'").fetchone()[0]
    p_count = cursor.execute("SELECT COUNT(*) FROM crops").fetchone()[0]
    c_count = cursor.execute("SELECT COUNT(DISTINCT state) FROM users").fetchone()[0] # Changed to state for regional accuracy
    conn.close()
    return render_template("index.html", counts={
        "farmers": f_count or 0,
        "buyers": b_count or 0,
        "products": p_count or 0,
        "countries": c_count or 1
    })

@app.route("/register")
def register():
    return render_template("registration.html")

@app.route("/post_register", methods=["POST"])
def post_register():
    data = request.form
    conn = sqlite3.connect("farmers.db")
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO users (user_type, name, country, state, district, phone, aadhar, password)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data.get('user_type'),
        data.get('name'),
        data.get('country'),
        data.get('state'),
        data.get('district'),
        data.get('phone'),
        data.get('aadhar'),
        data.get('password')
    ))
    conn.commit()
    conn.close()
    session['user_name'] = data.get('name')
    session['user_type'] = data.get('user_type')
    if data.get('user_type') == 'farmer':
        return redirect(url_for('sell_page'))
    else:
        return redirect(url_for('marketplace_page'))

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/post_login", methods=["POST"])
def post_login():
    name = request.form.get('name')
    pwd = request.form.get('password')
    conn = sqlite3.connect("farmers.db")
    cursor = conn.cursor()
    user = cursor.execute(
        "SELECT * FROM users WHERE name=? AND password=?",
        (name, pwd)
    ).fetchone()
    conn.close()
    if user:
        session['user_name'] = user[2]
        session['user_type'] = user[1]
        if user[1] == 'farmer':
            return redirect(url_for('sell_page'))
        else:
            return redirect(url_for('marketplace_page'))
    return "Invalid Details. <a href='/login'>Try Again</a>"

@app.route("/marketplace")
def marketplace_page():
    conn = sqlite3.connect("farmers.db")
    cursor = conn.cursor()
    crops = cursor.execute("SELECT * FROM crops").fetchall()
    conn.close()
    return render_template("marketplace.html", crops=crops)

# FIX: Updated endpoint name to 'crop_details' to match your HTML
@app.route("/crop_details/<int:crop_id>")
def crop_details(crop_id):
    conn = sqlite3.connect("farmers.db")
    cursor = conn.cursor()
    crop = cursor.execute("SELECT * FROM crops WHERE id=?", (crop_id,)).fetchone()
    conn.close()
    if crop:
        return render_template("crop_details.html", crop=crop)
    return "Crop not found", 404

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
    conn = sqlite3.connect("farmers.db")
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO crops (farmer_name, crop_name, quantity, price, location, crop_type, harvest_date, image_url, video_url)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        session['user_name'],
        request.form.get('crop_name'),
        request.form.get('quantity'),
        request.form.get('price'),
        request.form.get('location'),
        request.form.get('crop_type'),
        request.form.get('harvest_date'),
        img_fn,
        vid_fn
    ))
    conn.commit()
    conn.close()
    return redirect(url_for('marketplace_page'))

if __name__ == "__main__":
    app.run(debug=True)