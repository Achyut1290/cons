from flask_login import UserMixin

from config import get_db_connection


class User(UserMixin):
    def __init__(self, user_id, name, email, role="USER"):
        self.id = str(user_id)
        self.name = name
        self.email = email
        self.role = role

    @staticmethod
    def get_by_email(email):
        try:
            connection = get_db_connection()
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            user = cursor.fetchone()
            cursor.close()
            connection.close()
        except Exception:
            return None

        if not user:
            return None

        return User(
            user_id=user["id"],
            name=user["name"],
            email=user["email"],
            role=user.get("role", "USER"),
        )

    @staticmethod
    def get_by_id(user_id):
        try:
            connection = get_db_connection()
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
            user = cursor.fetchone()
            cursor.close()
            connection.close()
        except Exception:
            return None

        if not user:
            return None

        return User(
            user_id=user["id"],
            name=user["name"],
            email=user["email"],
            role=user.get("role", "USER"),
        )
