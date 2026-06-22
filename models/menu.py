from models.base_model import BaseModel


class Menu(BaseModel):
    """Model untuk tabel menu (data master 1)."""

    table_name = "menu"

    def all(self):
        # Override method all() milik BaseModel (polymorphism):
        # daftar menu disertai nama kategorinya
        return self.fetch_all(
            """
            SELECT m.*, k.nama_kategori
            FROM menu m
            LEFT JOIN kategori k ON m.id_kategori = k.id
            ORDER BY m.id
            """
        )

    def tersedia(self):
        # cuma menu aktif yang masih ada stoknya
        return self.fetch_all(
            "SELECT * FROM menu "
            "WHERE tersedia = 1 AND stok > 0 AND gambar IS NOT NULL AND gambar != ''"
        )

    def untuk_halaman(self):
        return self.fetch_all(
            """
            SELECT m.*, k.nama_kategori
            FROM menu m
            LEFT JOIN kategori k ON m.id_kategori = k.id
            WHERE m.tersedia = 1
            ORDER BY m.id
            """
        )

    def find_by_nama(self, nama):
        return self.fetch_one("SELECT * FROM menu WHERE nama_kopi = %s", (nama,))

    def set_gambar(self, id, gambar):
        """Isi gambar menu yang sebelumnya kosong (back-fill dari halaman menu)."""
        self.execute("UPDATE menu SET gambar = %s WHERE id = %s", (gambar, id))

    def delete(self, id):
        """Override delete (polymorphism): menu tetap bisa dihapus walau sudah
        pernah dipesan. Baris transaksi yang memakainya dibersihkan dulu, lalu
        total tiap pesanan terdampak dihitung ulang supaya tetap konsisten."""
        terdampak = self.fetch_all(
            "SELECT DISTINCT id_pesanan FROM detail_pesanan WHERE id_menu = %s", (id,)
        )
        self.execute("DELETE FROM detail_pesanan WHERE id_menu = %s", (id,))
        for r in terdampak:
            self.execute(
                """
                UPDATE pesanan p
                SET total_harga = COALESCE(
                    (SELECT SUM(dp.jumlah * dp.harga_satuan)
                     FROM detail_pesanan dp WHERE dp.id_pesanan = p.id), 0)
                WHERE p.id = %s
                """,
                (r["id_pesanan"],),
            )
        self.execute("DELETE FROM menu WHERE id = %s", (id,))

    def kurangi_stok(self, id, jumlah):
        """Kurangi stok saat pesanan di-checkout (tidak akan minus)."""
        self.execute(
            "UPDATE menu SET stok = GREATEST(stok - %s, 0) WHERE id = %s",
            (jumlah, id),
        )

    def tambah_stok(self, id, jumlah):
        """Kembalikan stok saat pesanan dibatalkan."""
        self.execute(
            "UPDATE menu SET stok = stok + %s WHERE id = %s",
            (jumlah, id),
        )

    def create(self, nama_kopi, harga, deskripsi=None, stok=0, gambar=None,
               id_kategori=None, tersedia=1):
        return self.execute(
            """
            INSERT INTO menu (nama_kopi, deskripsi, harga, stok, gambar, id_kategori, tersedia)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (nama_kopi, deskripsi, harga, stok, gambar, id_kategori, tersedia),
        )

    def update(self, id, nama_kopi, harga, deskripsi=None, stok=0, gambar=None,
               id_kategori=None, tersedia=1):
        self.execute(
            """
            UPDATE menu
            SET nama_kopi = %s, deskripsi = %s, harga = %s, stok = %s,
                gambar = %s, id_kategori = %s, tersedia = %s
            WHERE id = %s
            """,
            (nama_kopi, deskripsi, harga, stok, gambar, id_kategori, tersedia, id),
        )
