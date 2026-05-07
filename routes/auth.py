from flask import Blueprint
from flask import redirect, url_for
from flask import render_template, request, session, flash
from werkzeug.security import generate_password_hash, check_password_hash

from models.database import get_db_connection

auth_bp = Blueprint('auth', __name__)


# HOME
@auth_bp.route('/')
def home():
    return render_template('index.html')


# LOGIN
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['user_name'] = user['nama']
            session['role'] = user['role']
            flash('Login berhasil!', 'success')
            return redirect(url_for('auth.home'))
        flash('Email atau password salah!', 'error')
        return redirect(url_for('auth.login'))
    return render_template('login.html')


# REGISTER
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nama = request.form.get('nama')
        email = request.form.get('email')
        password = request.form.get('password')
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        if user:
            flash('Email sudah digunakan!', 'error')
            cursor.close()
            conn.close()
            return redirect(url_for('auth.register'))

        hashed = generate_password_hash(password)
        cursor.execute(
            "INSERT INTO users (nama, email, password) VALUES (%s, %s, %s)",
            (nama, email, hashed)
        )
        conn.commit()
        cursor.close()
        conn.close()
        flash('Akun berhasil dibuat!', 'success')
        return redirect(url_for('auth.login'))
    return render_template('register.html')


# LOGOUT
@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.home'))