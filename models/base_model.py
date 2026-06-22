from models.database import get_db_connection


class BaseModel:
    """
    Class induk semua model.
    Penerapan OOP:
    - Constructor (__init__) membuka koneksi database.
    - Encapsulation: koneksi disimpan di atribut private __conn,
      hanya bisa diakses lewat method class ini.
    - Polymorphism: atribut table_name di-override tiap subclass,
      sehingga method umum (all, find, delete) bekerja untuk tabel berbeda.
    """

    table_name = None  # di-override oleh subclass

    def __init__(self):
        self.__conn = get_db_connection()
        if self.__conn is None:
            raise ConnectionError("Tidak dapat terhubung ke database")

    def _cursor(self):
        return self.__conn.cursor(dictionary=True)

    def _commit(self):
        self.__conn.commit()

    def fetch_all(self, query, params=None):
        cursor = self._cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        cursor.close()
        return rows

    def fetch_one(self, query, params=None):
        cursor = self._cursor()
        cursor.execute(query, params)
        row = cursor.fetchone()
        cursor.close()
        return row

    def execute(self, query, params=None):
        cursor = self._cursor()
        cursor.execute(query, params)
        self._commit()
        last_id = cursor.lastrowid
        cursor.close()
        return last_id

    def all(self):
        return self.fetch_all(f"SELECT * FROM {self.table_name} ORDER BY id")

    def find(self, id):
        return self.fetch_one(
            f"SELECT * FROM {self.table_name} WHERE id = %s", (id,)
        )

    def delete(self, id):
        self.execute(f"DELETE FROM {self.table_name} WHERE id = %s", (id,))

    def count(self):
        row = self.fetch_one(f"SELECT COUNT(*) AS jumlah FROM {self.table_name}")
        return row["jumlah"]

    def close(self):
        if self.__conn:
            self.__conn.close()
            self.__conn = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
        return False
