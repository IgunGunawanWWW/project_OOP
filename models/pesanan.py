from models.base_model import BaseModel


class Pesanan(BaseModel):
    """Model untuk modul transaksi (tabel pesanan + detail_pesanan)."""

    table_name = "pesanan"

    # ---- keranjang ----
    def keranjang_aktif(self, id_user):
        return self.fetch_one(
            "SELECT * FROM pesanan WHERE id_user = %s AND status = 'pending'",
            (id_user,),
        )

    def buat_keranjang(self, id_user):
        return self.execute(
            "INSERT INTO pesanan (id_user, total_harga, status) VALUES (%s, 0, 'pending')",
            (id_user,),
        )

    def tambah_item(self, id_user, id_menu, jumlah, harga):
        keranjang = self.keranjang_aktif(id_user)
        if keranjang:
            id_pesanan = keranjang["id"]
        else:
            id_pesanan = self.buat_keranjang(id_user)

        # Gabungkan item kembar: kalau menu yang sama sudah ada di keranjang,
        # cukup tambah kuantitasnya supaya tetap satu baris per menu.
        existing = self.fetch_one(
            "SELECT id FROM detail_pesanan WHERE id_pesanan = %s AND id_menu = %s LIMIT 1",
            (id_pesanan, id_menu),
        )
        if existing:
            self.execute(
                "UPDATE detail_pesanan SET jumlah = jumlah + %s WHERE id = %s",
                (jumlah, existing["id"]),
            )
        else:
            self.execute(
                "INSERT INTO detail_pesanan (id_pesanan, id_menu, jumlah, harga_satuan) VALUES (%s, %s, %s, %s)",
                (id_pesanan, id_menu, jumlah, harga),
            )
        self.execute(
            "UPDATE pesanan SET total_harga = total_harga + %s WHERE id = %s",
            (harga * jumlah, id_pesanan),
        )
        return id_pesanan

    def _recalc_total(self, id_pesanan):
        """Hitung ulang total_harga dari detail agar selalu konsisten."""
        self.execute(
            """
            UPDATE pesanan p
            SET total_harga = COALESCE(
                (SELECT SUM(dp.jumlah * dp.harga_satuan)
                 FROM detail_pesanan dp WHERE dp.id_pesanan = p.id), 0)
            WHERE p.id = %s
            """,
            (id_pesanan,),
        )

    def set_jumlah(self, id_pesanan, id_menu, jumlah_baru):
        """Ubah kuantitas satu item di keranjang lalu hitung ulang total."""
        self.execute(
            "UPDATE detail_pesanan SET jumlah = %s WHERE id_pesanan = %s AND id_menu = %s",
            (jumlah_baru, id_pesanan, id_menu),
        )
        self._recalc_total(id_pesanan)

    def detail_untuk_stok(self, id_pesanan):
        """Pasangan (id_menu, jumlah) untuk penyesuaian stok."""
        return self.fetch_all(
            "SELECT id_menu, jumlah FROM detail_pesanan WHERE id_pesanan = %s",
            (id_pesanan,),
        )

    def items(self, id_pesanan):
        return self.fetch_all(
            """
            SELECT m.id AS id_menu, m.nama_kopi, m.gambar, k.nama_kategori AS kategori,
                   SUM(dp.jumlah) AS jumlah, dp.harga_satuan,
                   SUM(dp.jumlah * dp.harga_satuan) AS subtotal
            FROM detail_pesanan dp
            JOIN menu m ON dp.id_menu = m.id
            LEFT JOIN kategori k ON m.id_kategori = k.id
            WHERE dp.id_pesanan = %s
            GROUP BY m.id
            """,
            (id_pesanan,),
        )

    def hapus_item(self, id_pesanan, id_menu):
        item = self.fetch_one(
            "SELECT jumlah, harga_satuan FROM detail_pesanan WHERE id_pesanan = %s AND id_menu = %s LIMIT 1",
            (id_pesanan, id_menu),
        )
        if not item:
            return False

        subtotal = item["jumlah"] * item["harga_satuan"]
        self.execute(
            "DELETE FROM detail_pesanan WHERE id_pesanan = %s AND id_menu = %s LIMIT 1",
            (id_pesanan, id_menu),
        )
        self.execute(
            "UPDATE pesanan SET total_harga = total_harga - %s WHERE id = %s",
            (subtotal, id_pesanan),
        )
        return True

    def checkout(self, id_user):
        self.execute(
            "UPDATE pesanan SET status = 'diproses' WHERE id_user = %s AND status = 'pending'",
            (id_user,),
        )

    def checkout_with_stock(self, id_user):
        cursor = self.connection.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT id FROM pesanan
                WHERE id_user = %s AND status = 'pending'
                ORDER BY id DESC LIMIT 1
                FOR UPDATE
                """,
                (id_user,),
            )
            order = cursor.fetchone()
            if not order:
                self.connection.rollback()
                return None

            cursor.execute(
                "SELECT id_menu, jumlah FROM detail_pesanan WHERE id_pesanan = %s",
                (order["id"],),
            )
            details = cursor.fetchall()
            if not details:
                self.connection.rollback()
                return None

            for detail in details:
                cursor.execute(
                    """
                    UPDATE menu
                    SET stok = stok - %s
                    WHERE id = %s AND stok >= %s
                    """,
                    (detail["jumlah"], detail["id_menu"], detail["jumlah"]),
                )
                if cursor.rowcount != 1:
                    self.connection.rollback()
                    return None

            cursor.execute(
                "UPDATE pesanan SET status = 'diproses' WHERE id = %s",
                (order["id"],),
            )
            self.connection.commit()
            return order["id"]
        except Exception:
            self.connection.rollback()
            raise
        finally:
            cursor.close()

    # ---- pesanan milik user (untuk panel cart) ----
    def order_terkini(self, id_user):
        """Pesanan terakhir milik user (status apa pun), untuk panel cart."""
        return self.fetch_one(
            "SELECT * FROM pesanan WHERE id_user = %s ORDER BY id DESC LIMIT 1",
            (id_user,),
        )

    def ada_pesanan_diproses(self, id_user):
        """True jika user punya pesanan yang sedang diproses."""
        row = self.fetch_one(
            "SELECT id FROM pesanan WHERE id_user = %s AND status = 'diproses' LIMIT 1",
            (id_user,),
        )
        return row is not None

    def batalkan_diproses(self, id_user):
        """User membatalkan pesanannya yang sedang diproses.

        Hanya pesanan berstatus 'diproses' milik user yang bisa dibatalkan.
        Return True jika ada pesanan yang berhasil dibatalkan.
        """
        order = self.fetch_one(
            "SELECT id FROM pesanan WHERE id_user = %s AND status = 'diproses' ORDER BY id DESC LIMIT 1",
            (id_user,),
        )
        if not order:
            return False
        self.execute(
            "UPDATE pesanan SET status = 'dibatalkan' WHERE id = %s",
            (order["id"],),
        )
        return True

    def cancel_with_stock(self, id_user):
        cursor = self.connection.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT id FROM pesanan
                WHERE id_user = %s AND status = 'diproses'
                ORDER BY id DESC LIMIT 1
                FOR UPDATE
                """,
                (id_user,),
            )
            order = cursor.fetchone()
            if not order:
                self.connection.rollback()
                return None

            cursor.execute(
                "SELECT id_menu, jumlah FROM detail_pesanan WHERE id_pesanan = %s",
                (order["id"],),
            )
            for detail in cursor.fetchall():
                cursor.execute(
                    "UPDATE menu SET stok = stok + %s WHERE id = %s",
                    (detail["jumlah"], detail["id_menu"]),
                )
            cursor.execute(
                "UPDATE pesanan SET status = 'dibatalkan' WHERE id = %s",
                (order["id"],),
            )
            self.connection.commit()
            return order["id"]
        except Exception:
            self.connection.rollback()
            raise
        finally:
            cursor.close()

    def change_status_with_stock(self, order_id, status):
        cursor = self.connection.cursor(dictionary=True)
        try:
            cursor.execute(
                "SELECT status FROM pesanan WHERE id = %s FOR UPDATE",
                (order_id,),
            )
            order = cursor.fetchone()
            if not order:
                self.connection.rollback()
                return False

            old_consumed = order["status"] in ("diproses", "selesai")
            new_consumed = status in ("diproses", "selesai")
            if old_consumed != new_consumed:
                cursor.execute(
                    "SELECT id_menu, jumlah FROM detail_pesanan WHERE id_pesanan = %s",
                    (order_id,),
                )
                for detail in cursor.fetchall():
                    if new_consumed:
                        cursor.execute(
                            """
                            UPDATE menu SET stok = stok - %s
                            WHERE id = %s AND stok >= %s
                            """,
                            (detail["jumlah"], detail["id_menu"], detail["jumlah"]),
                        )
                        if cursor.rowcount != 1:
                            self.connection.rollback()
                            return False
                    else:
                        cursor.execute(
                            "UPDATE menu SET stok = stok + %s WHERE id = %s",
                            (detail["jumlah"], detail["id_menu"]),
                        )

            cursor.execute(
                "UPDATE pesanan SET status = %s WHERE id = %s",
                (status, order_id),
            )
            self.connection.commit()
            return True
        except Exception:
            self.connection.rollback()
            raise
        finally:
            cursor.close()

    def ubah_status(self, id, status):
        self.execute("UPDATE pesanan SET status = %s WHERE id = %s", (status, id))

    # ---- statistik dashboard ----
    def count_transaksi(self):
        # transaksi yang sudah di-checkout (bukan keranjang pending)
        row = self.fetch_one(
            "SELECT COUNT(*) AS jumlah FROM pesanan WHERE status != 'pending'"
        )
        return row["jumlah"]

    def total_pendapatan(self):
        row = self.fetch_one(
            """
            SELECT COALESCE(SUM(total_harga), 0) AS total
            FROM pesanan WHERE status IN ('diproses', 'selesai')
            """
        )
        return float(row["total"])

    def daftar_tahun(self):
        rows = self.fetch_all(
            "SELECT DISTINCT YEAR(created_at) AS tahun FROM pesanan ORDER BY tahun DESC"
        )
        return [r["tahun"] for r in rows]

    def rekap_per_bulan(self, tahun):
        """Total penjualan tiap bulan (Januari-Desember) pada tahun tertentu."""
        rows = self.fetch_all(
            """
            SELECT MONTH(created_at) AS bulan,
                   COALESCE(SUM(total_harga), 0) AS total
            FROM pesanan
            WHERE status IN ('diproses', 'selesai')
              AND YEAR(created_at) = %s
            GROUP BY MONTH(created_at)
            """,
            (tahun,),
        )
        per_bulan = {r["bulan"]: float(r["total"]) for r in rows}
        return [per_bulan.get(b, 0) for b in range(1, 13)]

    # ---- laporan ----
    def laporan(self, start=None, end=None):
        query = """
            SELECT p.id, p.created_at, p.total_harga, p.status,
                   u.nama AS nama_pelanggan, u.email,
                   COALESCE(GROUP_CONCAT(CONCAT(dp.jumlah, 'x ', m.nama_kopi)
                            SEPARATOR ', '), '-') AS daftar_item
            FROM pesanan p
            JOIN users u ON p.id_user = u.id
            LEFT JOIN detail_pesanan dp ON dp.id_pesanan = p.id
            LEFT JOIN menu m ON dp.id_menu = m.id
            WHERE p.status != 'pending'
        """
        params = []
        if start:
            query += " AND DATE(p.created_at) >= %s"
            params.append(start)
        if end:
            query += " AND DATE(p.created_at) <= %s"
            params.append(end)
        query += " GROUP BY p.id ORDER BY p.created_at DESC"
        return self.fetch_all(query, tuple(params) if params else None)

    def semua_dengan_detail(self):
        """Daftar transaksi + detail item, untuk tabel & drawer di dashboard."""
        pesanan = self.laporan()
        details = self.fetch_all(
            """
            SELECT dp.id_pesanan, m.nama_kopi AS name,
                   dp.harga_satuan AS price, dp.jumlah AS qty
            FROM detail_pesanan dp
            JOIN menu m ON dp.id_menu = m.id
            """
        )
        hasil = {}
        for p in pesanan:
            hasil[str(p["id"])] = {
                "date": p["created_at"].strftime("%d %b %Y, %H:%M"),
                "status": p["status"],
                "name": p["nama_pelanggan"],
                "email": p["email"],
                "items": [],
            }
        for d in details:
            key = str(d["id_pesanan"])
            if key in hasil:
                hasil[key]["items"].append(
                    {"name": d["name"], "price": float(d["price"]), "qty": d["qty"]}
                )
        return hasil
