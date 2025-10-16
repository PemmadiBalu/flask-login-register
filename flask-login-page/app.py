
from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # required for session management

# -------- DATABASE SETUP --------
def init_db():
    # Create the database file if it doesn't exist
    if not os.path.exists('database.db'):
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('''
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT,
                password TEXT NOT NULL
            )
        ''')
        conn.commit()
        conn.close()
        print("Database created and successfully connected")
    else:
        print("Database already exists and connected")

# -------- HOME ROUTE --------
@app.route('/')
def home():
    return redirect(url_for('login'))

# -------- REGISTER ROUTE --------
@app.route('/register', methods=['GET', 'POST'])
def register():
    message = ''
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        conn = sqlite3.connect('database.db')
        c = conn.cursor()

        try:
            c.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                      (username, email, password))
            conn.commit()
            message = 'Registration successful! Please login.'
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            message = 'Username already exists. Try another.'
        finally:
            conn.close()
    return render_template('register.html', message=message)

# -------- LOGIN ROUTE --------
@app.route('/login', methods=['GET', 'POST'])
def login():
    message = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = c.fetchone()
        conn.close()

        if user:
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            message = 'Invalid username or password!'
    return render_template('login.html', message=message)

# -------- DASHBOARD ROUTE --------
@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        return render_template('dashboard.html', username=session['username'])
    else:
        return redirect(url_for('login'))

# -------- LOGOUT ROUTE --------
@app.route('/logout', methods=['POST'])
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

# -------- MAIN --------
if __name__ == '__main__':
    init_db()  # create db & table if not exist
    app.run(debug=True)
# Run the app in debug mode for development purposes
