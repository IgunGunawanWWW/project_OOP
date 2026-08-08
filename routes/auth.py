from flask import Blueprint
from flask import redirect, url_for
from flask import render_template, request, session, flash
from flask import jsonify
from models.user import User
from models.menu import Menu
from models.pesanan import Pesanan

auth_bp = Blueprint('auth', __name__)


def _pesan_stok_kurang(menu, jumlah):
    """Return pesan error jika stok menu tidak mencukupi, atau None jika cukup."""
    stok = menu.get('stok') or 0
    if stok <= 0:
        return f"Stok {menu['nama_kopi']} sedang habis."
    if jumlah > stok:
        return f"Stok {menu['nama_kopi']} tinggal {stok}."
    return None


def _jumlah_valid(value):
    try:
        jumlah = int(value)
    except (TypeError, ValueError):
        return None
    return jumlah if jumlah > 0 else None


# HOME
@auth_bp.route('/')
def home():
    return render_template('home.html')


# LOGIN
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        with User() as model:
            user = model.find_by_email(email)
            if user and model.verify_password(user, password):
                session['user_id'] = user['id']
                session['user_name'] = user['nama']
                session['role'] = user['role']
                flash('Login berhasil!', 'success')
                if user['role'] == 'admin':
                    return redirect(url_for('admin.dashboard'))
                return redirect(url_for('auth.menu'))

        flash('Email atau password salah!', 'error')
        return redirect(url_for('auth.login'))
    return render_template('auth/login.html')


# REGISTER
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nama = request.form.get('nama')
        email = request.form.get('email')
        password = request.form.get('password')

        with User() as model:
            if model.find_by_email(email):
                flash('Email sudah digunakan!', 'error')
                return redirect(url_for('auth.register'))
            model.create(nama, email, password)

        flash('Akun berhasil dibuat!', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html')


# LOGOUT
@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.home'))


# HALAMAN MENU / TOKO
@auth_bp.route('/menu')
def menu():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    with Menu() as model:
        daftar_menu = model.untuk_halaman()

    return render_template('menu.html', menu=daftar_menu)


@auth_bp.route('/cart/add', methods=['POST'])
def cart_add():
    if 'user_id' not in session:
        return jsonify({'status': 'error', 'message': 'Belum login'})

    data = request.get_json(silent=True) or {}
    menu_id = data.get('menu_id')
    jumlah = _jumlah_valid(data.get('jumlah', 1))
    if not menu_id or jumlah is None:
        return jsonify({'status': 'error', 'message': 'Data menu atau jumlah tidak valid'}), 400

    with Menu() as menu_model, Pesanan() as pesanan_model:
        if pesanan_model.ada_pesanan_diproses(session['user_id']):
            return jsonify({'status': 'busy',
                            'message': 'Pesananmu sedang diproses. Tunggu sampai selesai untuk memesan lagi.'})

        menu = menu_model.find(menu_id)
        if not menu:
            return jsonify({'status': 'error', 'message': 'Menu tidak ditemukan'})

        kurang = _pesan_stok_kurang(menu, jumlah)
        if kurang:
            return jsonify({'status': 'habis', 'message': kurang})

        pesanan_model.tambah_item(session['user_id'], menu_id, jumlah, menu['harga'])

    return jsonify({'status': 'ok'})


@auth_bp.route('/cart')
def cart():
    if 'user_id' not in session:
        return jsonify({'status': 'error', 'message': 'Belum login'})

    with Pesanan() as model:
        order = model.order_terkini(session['user_id'])

        if not order:
            return jsonify({'status': 'ok', 'mode': 'empty', 'items': [], 'total': 0})

        status = order['status']

        # pending = keranjang yang sedang dibangun, diproses = pesanan aktif
        if status in ('pending', 'diproses'):
            items = [
                {
                    'id_menu': it['id_menu'],
                    'nama_kopi': it['nama_kopi'],
                    'gambar': it.get('gambar'),
                    'kategori': it.get('kategori'),
                    'jumlah': int(it['jumlah']),
                    'harga_satuan': float(it['harga_satuan']),
                    'subtotal': float(it['subtotal']),
                }
                for it in model.items(order['id'])
            ]
            if status == 'diproses':
                mode = 'diproses'
                # tandai pesanan ini sedang dipantau user
                session['active_order'] = order['id']
            else:
                mode = 'cart' if items else 'empty'
            return jsonify({
                'status': 'ok',
                'mode': mode,
                'order_id': order['id'],
                'items': items,
                'total': float(order['total_harga']),
            })

        # selesai / dibatalkan -> hanya tampilkan notifikasi sekali, yaitu untuk
        # pesanan yang tadi dipantau user. Pesanan lama yang sudah "ditutup"
        # tidak lagi muncul, jadi cart kembali kosong.
        if session.get('active_order') == order['id']:
            return jsonify({
                'status': 'ok',
                'mode': status,
                'order_id': order['id'],
                'items': [],
                'total': 0,
            })
        return jsonify({'status': 'ok', 'mode': 'empty', 'items': [], 'total': 0})


@auth_bp.route('/cart/cancel', methods=['POST'])
def cart_cancel():
    if 'user_id' not in session:
        return jsonify({'status': 'error', 'message': 'Belum login'})

    with Pesanan() as model:
        order_id = model.cancel_with_stock(session['user_id'])

    if not order_id:
        return jsonify({'status': 'error', 'message': 'Tidak ada pesanan yang bisa dibatalkan'})

    # tampilkan konfirmasi "dibatalkan" sekali untuk pesanan ini
    session['active_order'] = order_id
    return jsonify({'status': 'ok'})


@auth_bp.route('/cart/ack', methods=['POST'])
def cart_ack():
    """User menutup notifikasi pesanan selesai/dibatalkan ("Pesan Lagi"),
    sehingga cart kembali kosong dan siap untuk pesanan berikutnya."""
    session.pop('active_order', None)
    return jsonify({'status': 'ok'})


@auth_bp.route('/cart/add-by-name', methods=['POST'])
def cart_add_by_name():
    if 'user_id' not in session:
        return jsonify({'status': 'error', 'message': 'Belum login'})

    data = request.get_json(silent=True) or {}
    nama = str(data.get('nama', '')).strip()
    jumlah = _jumlah_valid(data.get('jumlah', 1))
    if not nama or jumlah is None:
        return jsonify({'status': 'error', 'message': 'Nama menu atau jumlah tidak valid'}), 400

    with Menu() as menu_model, Pesanan() as pesanan_model:
        if pesanan_model.ada_pesanan_diproses(session['user_id']):
            return jsonify({'status': 'busy',
                            'message': 'Pesananmu sedang diproses. Tunggu sampai selesai untuk memesan lagi.'})

        menu = menu_model.find_by_nama(nama)
        if not menu:
            return jsonify({'status': 'error', 'message': 'Menu tidak ditemukan'}), 404

        kurang = _pesan_stok_kurang(menu, jumlah)
        if kurang:
            return jsonify({'status': 'habis', 'message': kurang})

        pesanan_model.tambah_item(session['user_id'], menu['id'], jumlah, menu['harga'])

    return jsonify({'status': 'ok'})


@auth_bp.route('/cart/remove', methods=['POST'])
def cart_remove():
    if 'user_id' not in session:
        return jsonify({'status': 'error', 'message': 'Belum login'})

    data = request.get_json()
    nama = data.get('nama')

    with Menu() as menu_model, Pesanan() as pesanan_model:
        keranjang = pesanan_model.keranjang_aktif(session['user_id'])
        if not keranjang:
            return jsonify({'status': 'error', 'message': 'Tidak ada pesanan'})

        menu = menu_model.find_by_nama(nama)
        if not menu:
            return jsonify({'status': 'error', 'message': 'Menu tidak ditemukan'})

        if not pesanan_model.hapus_item(keranjang['id'], menu['id']):
            return jsonify({'status': 'error', 'message': 'Item tidak ada di keranjang'})

    return jsonify({'status': 'ok'})


@auth_bp.route('/cart/update-qty', methods=['POST'])
def cart_update_qty():
    if 'user_id' not in session:
        return jsonify({'status': 'error', 'message': 'Belum login'})

    data = request.get_json(silent=True) or {}
    nama = str(data.get('nama', '')).strip()
    jumlah = _jumlah_valid(data.get('jumlah', 1))
    if not nama or jumlah is None:
        return jsonify({'status': 'error', 'message': 'Kuantitas minimal 1'})

    with Menu() as menu_model, Pesanan() as pesanan_model:
        if pesanan_model.ada_pesanan_diproses(session['user_id']):
            return jsonify({'status': 'busy',
                            'message': 'Pesananmu sedang diproses. Tunggu sampai selesai untuk mengubah pesanan.'})

        keranjang = pesanan_model.keranjang_aktif(session['user_id'])
        if not keranjang:
            return jsonify({'status': 'error', 'message': 'Tidak ada pesanan'})

        menu = menu_model.find_by_nama(nama)
        if not menu:
            return jsonify({'status': 'error', 'message': 'Menu tidak ditemukan'})

        kurang = _pesan_stok_kurang(menu, jumlah)
        if kurang:
            return jsonify({'status': 'habis', 'message': kurang})

        pesanan_model.set_jumlah(keranjang['id'], menu['id'], jumlah)

    return jsonify({'status': 'ok'})


@auth_bp.route('/cart/checkout', methods=['POST'])
def cart_checkout():
    if 'user_id' not in session:
        return jsonify({'status': 'error'})

    with Pesanan() as model:
        order_id = model.checkout_with_stock(session['user_id'])

    # pantau pesanan ini supaya notifikasi selesai/dibatalkan muncul nanti
    if order_id:
        session['active_order'] = order_id

    if not order_id:
        return jsonify({'status': 'error', 'message': 'Keranjang kosong atau stok tidak mencukupi'}), 409
    return jsonify({'status': 'ok'})
