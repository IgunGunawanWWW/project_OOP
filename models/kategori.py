from models.base_model import BaseModel


class Kategori(BaseModel):
    """Model untuk tabel kategori (data master 2)."""

    table_name = "kategori"

    def create(self, nama_kategori):
        return self.execute(
            "INSERT INTO kategori (nama_kategori) VALUES (%s)", (nama_kategori,)
        )

    def update(self, id, nama_kategori):
        self.execute(
            "UPDATE kategori SET nama_kategori = %s WHERE id = %s",
            (nama_kategori, id),
        )
