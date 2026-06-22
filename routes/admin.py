from datetime import date
from functools import wraps
import mysql.connector
from flask import Blueprint
from flask import redirect, url_for
from flask import render_template, request, session, flash
from flask import jsonify
from models.user import User
from models.menu import Menu
from models.kategori import Kategori
from models.pesanan import Pesanan

admin_bp = Blueprint('admin', __name__)


def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        if session.get('role') != 'admin':
            flash('Halaman khusus admin!', 'error')
            return redirect(url_for('auth.menu'))
        return f(*args, **kwargs)
    return wrapper


# ============ DASHBOARD ============
@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    with Menu() as menu_model, User() as user_model, \
            Kategori() as kategori_model, Pesanan() as pesanan_model:
        stats = {
            'jumlah_menu': menu_model.count(),
            'jumlah_kategori': kategori_model.count(),
            'jumlah_pelanggan': user_model.count_pelanggan(),
            'jumlah_transaksi': pesanan_model.count_transaksi(),
            'total_pendapatan': pesanan_model.total_pendapatan(),
        }
        tahun_tersedia = pesanan_model.daftar_tahun() or [date.today().year]
        tahun = request.args.get('tahun', type=int)
        if tahun not in tahun_tersedia:
            tahun = tahun_tersedia[0]
        rekap = pesanan_model.rekap_per_bulan(tahun)
        transaksi = pesanan_model.semua_dengan_detail()

    chart = {
        'labels': ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun',
                   'Jul', 'Agu', 'Sep', 'Okt', 'Nov', 'Des'],
        'data': rekap,
    }
    return render_template('admin/dashboard.html', stats=stats, chart=chart,
                           transaksi=transaksi, tahun=tahun,
                           tahun_tersedia=tahun_tersedia)


@admin_bp.route('/admin/pesanan/<int:id>/status', methods=['POST'])
@admin_required
def pesanan_status(id):
    status = request.get_json().get('status')
    if status not in ('pending', 'diproses', 'selesai', 'dibatalkan'):
        return jsonify({'status': 'error', 'message': 'Status tidak valid'})
    with Pesanan() as model, Menu() as menu_model:
        order = model.find(id)
        if not order:
            return jsonify({'status': 'error', 'message': 'Pesanan tidak ditemukan'})

        lama = order['status']
        if lama != status:
            # stok dipotong saat 'diproses'/'selesai', dikembalikan saat batal/pending
            dulu_terpotong = lama in ('diproses', 'selesai')
            kini_terpotong = status in ('diproses', 'selesai')
            if dulu_terpotong and not kini_terpotong:
                for d in model.detail_untuk_stok(id):
                    menu_model.tambah_stok(d['id_menu'], d['jumlah'])
            elif not dulu_terpotong and kini_terpotong:
                for d in model.detail_untuk_stok(id):
                    menu_model.kurangi_stok(d['id_menu'], d['jumlah'])

        model.ubah_status(id, status)
    return jsonify({'status': 'ok'})


# ============ LAPORAN ============
@admin_bp.route('/laporan')
@admin_required
def laporan():
    start = request.args.get('start') or None
    end = request.args.get('end') or None

    with Pesanan() as model:
        daftar = model.laporan(start, end)

    rekap = {
        'jumlah': len(daftar),
        'total': sum(float(p['total_harga']) for p in daftar
                     if p['status'] != 'dibatalkan'),
    }
    return render_template('admin/laporan.html', daftar=daftar, rekap=rekap,
                           start=start or '', end=end or '')


# ============ MANAJEMEN USER ============
@admin_bp.route('/admin/users')
@admin_required
def users():
    edit_id = request.args.get('edit', type=int)
    with User() as model:
        daftar = model.all()
        edit_user = model.find(edit_id) if edit_id else None
    return render_template('admin/users.html', daftar=daftar, edit_user=edit_user)


@admin_bp.route('/admin/users/tambah', methods=['POST'])
@admin_required
def users_tambah():
    with User() as model:
        if model.find_by_email(request.form['email']):
            flash('Email sudah digunakan!', 'error')
        else:
            model.create(request.form['nama'], request.form['email'],
                         request.form['password'], request.form['role'])
            flash('User berhasil ditambahkan!', 'success')
    return redirect(url_for('admin.users'))


@admin_bp.route('/admin/users/<int:id>/edit', methods=['POST'])
@admin_required
def users_edit(id):
    with User() as model:
        model.update(id, request.form['nama'], request.form['email'],
                     request.form['role'], request.form.get('password') or None)
    flash('User berhasil diubah!', 'success')
    return redirect(url_for('admin.users'))


@admin_bp.route('/admin/users/<int:id>/hapus', methods=['POST'])
@admin_required
def users_hapus(id):
    if id == session['user_id']:
        flash('Tidak bisa menghapus akun sendiri!', 'error')
        return redirect(url_for('admin.users'))
    try:
        with User() as model:
            model.delete(id)
        flash('User berhasil dihapus!', 'success')
    except mysql.connector.Error:
        flash('User tidak bisa dihapus karena memiliki transaksi!', 'error')
    return redirect(url_for('admin.users'))


# ============ CRUD MENU (DATA MASTER 1) ============
@admin_bp.route('/admin/menu')
@admin_required
def menu():
    edit_id = request.args.get('edit', type=int)
    with Menu() as model, Kategori() as kategori_model:
        daftar = model.all()
        kategori = kategori_model.all()
        edit_menu = model.find(edit_id) if edit_id else None
    return render_template('admin/menu.html', daftar=daftar, kategori=kategori,
                           edit_menu=edit_menu)


def _form_menu():
    return {
        'nama_kopi': request.form['nama_kopi'],
        'harga': request.form['harga'],
        'deskripsi': request.form.get('deskripsi') or None,
        'stok': request.form.get('stok', 0),
        'gambar': request.form.get('gambar') or None,
        'id_kategori': request.form.get('id_kategori') or None,
        'tersedia': 1 if request.form.get('tersedia') else 0,
    }


@admin_bp.route('/admin/menu/tambah', methods=['POST'])
@admin_required
def menu_tambah():
    with Menu() as model:
        model.create(**_form_menu())
    flash('Menu berhasil ditambahkan!', 'success')
    return redirect(url_for('admin.menu'))


@admin_bp.route('/admin/menu/<int:id>/edit', methods=['POST'])
@admin_required
def menu_edit(id):
    with Menu() as model:
        model.update(id, **_form_menu())
    flash('Menu berhasil diubah!', 'success')
    return redirect(url_for('admin.menu'))


@admin_bp.route('/admin/menu/<int:id>/hapus', methods=['POST'])
@admin_required
def menu_hapus(id):
    try:
        with Menu() as model:
            model.delete(id)
        flash('Menu berhasil dihapus!', 'success')
    except mysql.connector.Error:
        flash('Menu gagal dihapus. Coba lagi.', 'error')
    return redirect(url_for('admin.menu'))


# ============ CRUD KATEGORI (DATA MASTER 2) ============
@admin_bp.route('/admin/kategori')
@admin_required
def kategori():
    edit_id = request.args.get('edit', type=int)
    with Kategori() as model:
        daftar = model.all()
        edit_kategori = model.find(edit_id) if edit_id else None
    return render_template('admin/kategori.html', daftar=daftar,
                           edit_kategori=edit_kategori)


@admin_bp.route('/admin/kategori/tambah', methods=['POST'])
@admin_required
def kategori_tambah():
    with Kategori() as model:
        model.create(request.form['nama_kategori'])
    flash('Kategori berhasil ditambahkan!', 'success')
    return redirect(url_for('admin.kategori'))


@admin_bp.route('/admin/kategori/<int:id>/edit', methods=['POST'])
@admin_required
def kategori_edit(id):
    with Kategori() as model:
        model.update(id, request.form['nama_kategori'])
    flash('Kategori berhasil diubah!', 'success')
    return redirect(url_for('admin.kategori'))


@admin_bp.route('/admin/kategori/<int:id>/hapus', methods=['POST'])
@admin_required
def kategori_hapus(id):
    try:
        with Kategori() as model:
            model.delete(id)
        flash('Kategori berhasil dihapus!', 'success')
    except mysql.connector.Error:
        flash('Kategori tidak bisa dihapus karena masih dipakai menu!', 'error')
    return redirect(url_for('admin.kategori'))
