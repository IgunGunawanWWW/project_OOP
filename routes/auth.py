from flask import Blueprint
from flask import redirect, url_for
from flask import render_template, request, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask import jsonify
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
            return redirect(url_for('auth.main'))
        flash('Email atau password salah!', 'error')
        return redirect(url_for('auth.home'))
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

# main.html
@auth_bp.route('/main')
def main():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM menu WHERE tersedia = 1 AND gambar IS NOT NULL AND gambar != ''")
    menu = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('main.html', menu=menu)
@auth_bp.route('/cart/add', methods=['POST'])
def cart_add():
    if 'user_id' not in session:
        return jsonify({'status': 'error', 'message': 'Belum login'})

    data = request.get_json()
    menu_id = data.get('menu_id')
    jumlah = data.get('jumlah', 1)

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Ambil harga menu
    cursor.execute("SELECT harga FROM menu WHERE id = %s", (menu_id,))
    menu = cursor.fetchone()
    if not menu:
        return jsonify({'status': 'error', 'message': 'Menu tidak ditemukan'})

    harga = menu['harga']

    # Cek apakah ada pesanan pending milik user
    cursor.execute(
        "SELECT id FROM pesanan WHERE id_user = %s AND status = 'pending'",
        (session['user_id'],)
    )
    pesanan = cursor.fetchone()

    if pesanan:
        pesanan_id = pesanan['id']
    else:
        # Buat pesanan baru
        cursor.execute(
            "INSERT INTO pesanan (id_user, total_harga, status) VALUES (%s, %s, 'pending')",
            (session['user_id'], 0)
        )
        conn.commit()
        pesanan_id = cursor.lastrowid

    # Tambah ke detail_pesanan
    cursor.execute(
        "INSERT INTO detail_pesanan (id_pesanan, id_menu, jumlah, harga_satuan) VALUES (%s, %s, %s, %s)",
        (pesanan_id, menu_id, jumlah, harga)
    )

    # Update total_harga di pesanan
    cursor.execute(
        "UPDATE pesanan SET total_harga = total_harga + %s WHERE id = %s",
        (harga * jumlah, pesanan_id)
    )

    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({'status': 'ok'})


@auth_bp.route('/cart')
def cart():
    if 'user_id' not in session:
        return jsonify({'status': 'error', 'message': 'Belum login'})

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM pesanan WHERE id_user = %s AND status = 'pending'",
        (session['user_id'],)
    )
    pesanan = cursor.fetchone()

    if not pesanan:
        return jsonify({'status': 'ok', 'items': [], 'total': 0})

    cursor.execute("""
        SELECT m.nama_kopi, dp.jumlah, dp.harga_satuan,
               (dp.jumlah * dp.harga_satuan) AS subtotal
        FROM detail_pesanan dp
        JOIN menu m ON dp.id_menu = m.id
        WHERE dp.id_pesanan = %s
    """, (pesanan['id'],))

    items = cursor.fetchall()
    cursor.close()
    conn.close()

    return jsonify({
        'status': 'ok',
        'items': items,
        'total': float(pesanan['total_harga'])
    })

@auth_bp.route('/cart/add-by-name', methods=['POST'])
def cart_add_by_name():
    if 'user_id' not in session:
        return jsonify({'status': 'error', 'message': 'Belum login'})
    data = request.get_json()
    nama = data.get('nama')
    harga = data.get('harga')
    jumlah = data.get('jumlah', 1)  # Sudah ada, pastikan terbaca
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Cari menu di database, kalau belum ada otomatis ditambahkan
    cursor.execute("SELECT id FROM menu WHERE nama_kopi = %s", (nama,))
    menu = cursor.fetchone()

    if not menu:
        cursor.execute(
            "INSERT INTO menu (nama_kopi, harga, tersedia) VALUES (%s, %s, 1)",
            (nama, harga)
        )
        conn.commit()
        menu_id = cursor.lastrowid
    else:
        menu_id = menu['id']

    # Cek pesanan pending milik user
    cursor.execute(
        "SELECT id FROM pesanan WHERE id_user = %s AND status = 'pending'",
        (session['user_id'],)
    )
    pesanan = cursor.fetchone()

    if pesanan:
        pesanan_id = pesanan['id']
    else:
        cursor.execute(
            "INSERT INTO pesanan (id_user, total_harga, status) VALUES (%s, %s, 'pending')",
            (session['user_id'], 0)
        )
        conn.commit()
        pesanan_id = cursor.lastrowid

    cursor.execute(
        "INSERT INTO detail_pesanan (id_pesanan, id_menu, jumlah, harga_satuan) VALUES (%s, %s, %s, %s)",
        (pesanan_id, menu_id, jumlah, harga)
    )
    cursor.execute(
        "UPDATE pesanan SET total_harga = total_harga + %s WHERE id = %s",
        (harga * jumlah, pesanan_id)
    )
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({'status': 'ok'})

@auth_bp.route('/cart/remove', methods=['POST'])
def cart_remove():
    if 'user_id' not in session:
        return jsonify({'status': 'error', 'message': 'Belum login'})

    data = request.get_json()
    nama = data.get('nama')

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Cari pesanan pending milik user
    cursor.execute(
        "SELECT id FROM pesanan WHERE id_user = %s AND status = 'pending'",
        (session['user_id'],)
    )
    pesanan = cursor.fetchone()
    if not pesanan:
        return jsonify({'status': 'error', 'message': 'Tidak ada pesanan'})

    # Cari menu
    cursor.execute("SELECT id FROM menu WHERE nama_kopi = %s", (nama,))
    menu = cursor.fetchone()
    if not menu:
        return jsonify({'status': 'error', 'message': 'Menu tidak ditemukan'})

    # Ambil data item sebelum dihapus untuk update total
    cursor.execute(
        "SELECT jumlah, harga_satuan FROM detail_pesanan WHERE id_pesanan = %s AND id_menu = %s LIMIT 1",
        (pesanan['id'], menu['id'])
    )
    item = cursor.fetchone()
    if not item:
        return jsonify({'status': 'error', 'message': 'Item tidak ada di keranjang'})

    subtotal = item['jumlah'] * item['harga_satuan']

    # Hapus item
    cursor.execute(
        "DELETE FROM detail_pesanan WHERE id_pesanan = %s AND id_menu = %s LIMIT 1",
        (pesanan['id'], menu['id'])
    )

    # Update total
    cursor.execute(
        "UPDATE pesanan SET total_harga = total_harga - %s WHERE id = %s",
        (subtotal, pesanan['id'])
    )

    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({'status': 'ok'})

@auth_bp.route('/cart/checkout', methods=['POST'])
def cart_checkout():
    if 'user_id' not in session:
        return jsonify({'status': 'error'})

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "UPDATE pesanan SET status = 'diproses' WHERE id_user = %s AND status = 'pending'",
        (session['user_id'],)
    )
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({'status': 'ok'})