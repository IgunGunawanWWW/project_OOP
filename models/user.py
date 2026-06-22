from werkzeug.security import generate_password_hash, check_password_hash
from models.base_model import BaseModel


class User(BaseModel):
    """Model untuk tabel users (inheritance dari BaseModel)."""

    table_name = "users"

    def find_by_email(self, email):
        return self.fetch_one("SELECT * FROM users WHERE email = %s", (email,))

    def create(self, nama, email, password, role="pelanggan"):
        hashed = generate_password_hash(password)
        return self.execute(
            "INSERT INTO users (nama, email, password, role) VALUES (%s, %s, %s, %s)",
            (nama, email, hashed, role),
        )

    def update(self, id, nama, email, role, password=None):
        if password:
            self.execute(
                "UPDATE users SET nama = %s, email = %s, role = %s, password = %s WHERE id = %s",
                (nama, email, role, generate_password_hash(password), id),
            )
        else:
            self.execute(
                "UPDATE users SET nama = %s, email = %s, role = %s WHERE id = %s",
                (nama, email, role, id),
            )

    def verify_password(self, user, password):
        return check_password_hash(user["password"], password)

    def count_pelanggan(self):
        row = self.fetch_one(
            "SELECT COUNT(*) AS jumlah FROM users WHERE role = 'pelanggan'"
        )
        return row["jumlah"]
