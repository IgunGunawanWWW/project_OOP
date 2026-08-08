# ☕ Fabulous Coffee

## Dokumentasi
[Google Drive](https://drive.google.com/drive/folders/1SsQkaXwFn7ZLpW0MVeBgmV8F1xaYMpFY)
Gunakan akun ubm untuk mengakses


Dibangun dengan **Flask** + **MySQL/MariaDB** sebagai project akhir mata kuliah
**Pemrograman Berorientasi Objek (OOP)**. Struktur kodenya menekankan penerapan
konsep OOP (inheritance, encapsulation, polymorphism) pada layer model/database.

Aplikasi memiliki dua sisi:

- **Pelanggan** — melihat menu, menambah ke keranjang, checkout, dan memantau status pesanan.
- **Admin** — dashboard statistik & grafik penjualan, kelola menu, kategori, user, serta laporan transaksi.

---

## 👥 Tim Pengembang

| Nama | NIM |
|------|-----|
| Vio Lefrans | 32250095 |
| Igun Gunawan | 32250094 |
| Kelvin Filemon | 32250077 |

---

## ✨ Fitur

### Pelanggan
- 🔐 Register & Login dengan password hashing (`werkzeug.security`).
- 🎠 Slider best seller yang smooth & infinite.
- 📋 Menu dinamis dari database, dikelompokkan per kategori (Coffee, Non-Coffee, Snack, Food).
- 🔍 Detail produk dengan gambar.
- 🛒 Keranjang real-time: tambah item, ubah kuantitas, hapus item.
- 📦 Validasi stok otomatis (tidak bisa memesan melebihi stok).
- ✅ Checkout & pemantauan status pesanan (pending → diproses → selesai/dibatalkan).
- ↩️ Pembatalan pesanan oleh pelanggan (stok dikembalikan otomatis).
- 👤 Navbar menampilkan nama user yang sedang login.

### Admin
- 📊 **Dashboard**: jumlah menu, kategori, pelanggan, transaksi, total pendapatan, dan grafik penjualan per bulan.
- ☕ **Manajemen Menu** (data master 1): CRUD lengkap + stok, gambar, kategori, status tersedia.
- 🏷️ **Manajemen Kategori** (data master 2): CRUD kategori.
- 👥 **Manajemen User**: CRUD user beserta peran (admin/pelanggan).
- 🧾 **Laporan Transaksi**: filter berdasarkan rentang tanggal + rekap total.
- 🔄 Ubah status pesanan dengan penyesuaian stok otomatis.

---

## 🛠️ Teknologi

| Teknologi | Kegunaan |
|-----------|----------|
| Python 3 | Backend |
| Flask (Blueprint) | Web Framework |
| MySQL / MariaDB | Database |
| mysql-connector-python | Koneksi Python ke MySQL |
| Werkzeug | Password hashing |
| python-dotenv | Environment variable (`.env`) |
| HTML / CSS / JS | Frontend |
| Font Awesome | Icon |
| Google Fonts | Playfair Display & Montserrat |

---

## 🧩 Penerapan Konsep OOP

Layer model dirancang untuk menunjukkan konsep OOP secara nyata:

- **Inheritance** — semua model (`User`, `Menu`, `Kategori`, `Pesanan`) mewarisi
  [`BaseModel`](models/base_model.py) yang menyediakan operasi umum (`all`, `find`, `delete`, `count`).
- **Encapsulation** — koneksi database disimpan pada atribut privat `__conn` di `BaseModel`
  dan hanya diakses lewat method internal class.
- **Polymorphism** — atribut `table_name` di-_override_ tiap subclass, dan method seperti
  `all()` / `delete()` di-_override_ (mis. `Menu.all()` ikut mengambil nama kategori).
- **Context manager** — setiap model memakai `with ... as model:` (`__enter__`/`__exit__`)
  agar koneksi database otomatis ditutup.

---

## 📁 Struktur Project

```
struktur website
├── 📁 models/
│   ├── 🐍 base_model.py
│   ├── 🐍 database.py
│   ├── 🐍 kategori.py
│   ├── 🐍 menu.py
│   ├── 🐍 pesanan.py
│   └── 🐍 user.py
├── 📁 routes/
│   ├── 🐍 admin.py
│   └── 🐍 auth.py
├── 📁 sql/
│   └── 📄 kopi_db.sql
├── 📁 static/
│   ├── 📁 CSS/
│   │   ├── 🎨 style.css
│   │   └── 🎨 style_main.css
│   ├── 📁 images/
│   │   ├── 📁 coffee/
│   │   │   ├── 🖼️ Hazelnut_Latte.webp
│   │   │   ├── 🖼️ affogato.webp
│   │   │   ├── 🖼️ americano.webp
│   │   │   ├── 🖼️ cafe_latte.webp
│   │   │   └── 🖼️ mochaccino.webp
│   │   ├── 📁 food/
│   │   │   ├── 🖼️ beef_burger.webp
│   │   │   ├── 🖼️ mie_ayam.webp
│   │   │   ├── 🖼️ nasi_goreng.webp
│   │   │   └── 🖼️ pasta_carbonara.webp
│   │   ├── 📁 menu/
│   │   │   ├── 🖼️ Caramel_Latte_RMBG.webp
│   │   │   ├── 🖼️ Dalgona_Coffee_RMBG.webp
│   │   │   ├── 🖼️ Vanilla_Latte_RMBG.webp
│   │   │   ├── 🖼️ bg.webp
│   │   │   └── 🖼️ logo.webp
│   │   ├── 📁 non-coffee/
│   │   │   ├── 🖼️ chocolate.webp
│   │   │   ├── 🖼️ cookies_cream.webp
│   │   │   ├── 🖼️ matcha_latte.webp
│   │   │   ├── 🖼️ red_velvet.webp
│   │   │   └── 🖼️ taro_latte.webp
│   │   └── 📁 snack/
│   │       ├── 🖼️ butter_croissant.webp
│   │       ├── 🖼️ cireng_glazed.webp
│   │       ├── 🖼️ donut_glazed.webp
│   │       └── 🖼️ french_fries.webp
│   └── 📁 js/
│       └── 📄 script.js
├── 📁 templates/
│   ├── 📁 admin/
│   │   ├── 🌐 base.html
│   │   ├── 🌐 dashboard.html
│   │   ├── 🌐 kategori.html
│   │   ├── 🌐 laporan.html
│   │   ├── 🌐 menu.html
│   │   └── 🌐 users.html
│   ├── 📁 auth/
│   │   ├── 🌐 login.html
│   │   └── 🌐 register.html
│   ├── 🌐 home.html
│   └── 🌐 menu.html
└── 🐍 main.py
```

---

## 🗄️ Struktur Database

Database `kopi_db` terdiri dari **5 tabel** yang saling berelasi.

### `users`
| Kolom        | Tipe                          | Keterangan                       |
| ------------ | ----------------------------- | -------------------------------- |
| `id`         | INT, PK, AUTO_INCREMENT       | ID user                          |
| `nama`       | VARCHAR(100)                  | Nama lengkap                     |
| `email`      | VARCHAR(100), UNIQUE          | Email (untuk login)              |
| `password`   | VARCHAR(255)                  | Password ter-_hash_              |
| `role`       | ENUM('admin','pelanggan')     | Peran user (default `pelanggan`) |
| `created_at` | TIMESTAMP                     | Waktu pendaftaran                |

### `kategori`
| Kolom           | Tipe                    | Keterangan          |
| --------------- | ----------------------- | ------------------- |
| `id`            | INT, PK, AUTO_INCREMENT | ID kategori         |
| `nama_kategori` | VARCHAR(50)             | Nama kategori menu  |

### `menu` (data master)
| Kolom         | Tipe                    | Keterangan                                  |
| ------------- | ----------------------- | ------------------------------------------- |
| `id`          | INT, PK, AUTO_INCREMENT | ID menu                                     |
| `nama_kopi`   | VARCHAR(100)            | Nama menu                                    |
| `deskripsi`   | TEXT                    | Deskripsi menu                              |
| `harga`       | DECIMAL(10,2)           | Harga satuan                                |
| `stok`        | INT                     | Jumlah stok                                 |
| `gambar`      | VARCHAR(255)            | Path gambar (relatif terhadap `static/`)    |
| `id_kategori` | INT, FK → `kategori.id` | Kategori menu                               |
| `tersedia`    | TINYINT(1)              | Status tampil di halaman menu (1 = tampil)  |

### `pesanan`
| Kolom         | Tipe                                              | Keterangan                  |
| ------------- | ------------------------------------------------ | --------------------------- |
| `id`          | INT, PK, AUTO_INCREMENT                          | ID pesanan                  |
| `id_user`     | INT, FK → `users.id`                             | Pemesan                     |
| `total_harga` | DECIMAL(10,2)                                    | Total harga pesanan         |
| `status`      | ENUM('pending','diproses','selesai','dibatalkan') | Status pesanan (default `pending` = keranjang) |
| `created_at`  | TIMESTAMP                                        | Waktu pesanan dibuat        |

### `detail_pesanan`
| Kolom          | Tipe                      | Keterangan                  |
| -------------- | ------------------------- | --------------------------- |
| `id`           | INT, PK, AUTO_INCREMENT   | ID detail                   |
| `id_pesanan`   | INT, FK → `pesanan.id`    | Pesanan terkait             |
| `id_menu`      | INT, FK → `menu.id`       | Menu yang dipesan           |
| `jumlah`       | INT                       | Kuantitas                   |
| `harga_satuan` | DECIMAL(10,2)             | Harga satuan saat dipesan   |

**Relasi:**

```
users (1) ───< pesanan (1) ───< detail_pesanan >─── (1) menu >─── (1) kategori
```

---

## 📦 Instalasi & Setup

### 1. Clone repository
```bash
git clone https://github.com/IgunGunawanWWW/project_OOP.git
cd project_OOP
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Jalankan MySQL / MariaDB
Pastikan service **MySQL** (mis. lewat XAMPP) sudah berjalan.

### 4. Setup database
Import skema + data awal lewat phpMyAdmin / MySQL Workbench, atau jalankan:
```bash
mysql -u root -p < sql/kopi_db.sql
```
File `sql/kopi_db.sql` sudah membuat database `kopi_db` beserta seluruh tabel dan data awalnya.

### 5. Buat file `.env`
Buat file `.env` di root folder (sejajar dengan `main.py`):
```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=
DB_NAME=kopi_db
FLASK_SECRET_KEY=ganti-dengan-nilai-random-yang-panjang
```
> Sesuaikan `DB_PASSWORD` jika MySQL kamu menggunakan password.
> Jangan commit `.env`; gunakan secret yang berbeda untuk setiap environment.

### 6. Jalankan aplikasi
```bash
python main.py
```
Buka browser ke **http://127.0.0.1:5000**

---

## 👤 Akun Bawaan

Database awal sudah berisi akun admin & beberapa pelanggan:

| Peran     | Email             |
| --------- | ----------------- |
| Admin     | `admin@kopi.com`  |
| Pelanggan | `budi@gmail.com`  |

> Password tersimpan dalam bentuk _hash_ dan tidak bisa dibaca langsung di database.
> Jika tidak mengetahui password akun bawaan, daftarkan akun baru lewat halaman
> **Register** (akun baru otomatis berperan `pelanggan`).

---

## 🧭 Ringkasan Route

| Route                          | Method     | Akses     | Fungsi                          |
| ------------------------------ | ---------- | --------- | ------------------------------- |
| `/`                            | GET        | Publik    | Halaman utama                   |
| `/login`, `/register`          | GET, POST  | Publik    | Autentikasi                     |
| `/logout`                      | GET        | User      | Keluar                          |
| `/menu`                        | GET        | Pelanggan | Halaman menu / toko             |
| `/cart`, `/cart/...`           | GET, POST  | Pelanggan | Keranjang & checkout            |
| `/dashboard`                   | GET        | Admin     | Dashboard & statistik           |
| `/admin/menu`, `/admin/kategori`, `/admin/users` | GET, POST | Admin | CRUD data master          |
| `/laporan`                     | GET        | Admin     | Laporan transaksi               |

---

## 🚀 Cara Penggunaan

1. Buka `http://127.0.0.1:5000`
2. Klik **Daftar** untuk membuat akun baru
3. **Login** dengan email dan password
4. Browse menu — klik card untuk melihat detail & pilih jumlah
5. Klik **+** untuk langsung tambah ke keranjang
6. Buka ikon 🛒 untuk melihat pesanan
7. Klik **Checkout** untuk menyelesaikan pesanan
8. Login sebagai **admin** untuk mengakses dashboard & manajemen data

---

## ⚠️ Catatan Penting

- Password tersimpan dalam bentuk **hash** — tidak bisa dibaca langsung di database.
- Pastikan service MySQL berjalan sebelum menjalankan `python main.py`.
- Folder `__pycache__/` dan file `*.pyc` di-_ignore_ lewat `.gitignore`.
- File `.env` pada repo ini hanya berisi konfigurasi lokal (development). Untuk produksi,
  ganti kredensial dan jangan commit `.env` yang berisi data sensitif.

---

© 2026 Fabulous Coffee. All Rights Reserved.
