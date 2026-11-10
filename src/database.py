import sqlite3


class DatabaseRepository:
    def __init__(self, db_path: str):
        self.connection = sqlite3.connect(db_path)
        self.connection.row_factory = sqlite3.Row
        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS comments (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL CHECK(length(name) <= 256),
                message TEXT NOT NULL CHECK(length(message) <= 8096)
            )
            """
        )
        self.connection.commit()

    @staticmethod
    def _check_id(comment_id):
        if type(comment_id) is not int:
            raise TypeError("ID должен быть целым числом.")

    @staticmethod
    def _check_text(value, limit, field):
        if not isinstance(value, str):
            raise TypeError(f"{field}: ожидается строка.")
        if len(value) > limit:
            raise ValueError(f"{field}: максимум {limit} символов.")

    def get_by_id(self, comment_id: int):
        self._check_id(comment_id)
        row = self.connection.execute(
            "SELECT id, name, message FROM comments WHERE id = ?",
            (comment_id,),
        ).fetchone()
        return dict(row) if row is not None else None

    def get_by_name(self, username: str):
        self._check_text(username, 256, "Имя")
        rows = self.connection.execute(
            "SELECT id, name, message FROM comments WHERE name = ? ORDER BY id",
            (username,),
        ).fetchall()
        return [dict(row) for row in rows]

    def add(self, comment_id: int, username: str, message: str) -> bool:
        self._check_id(comment_id)
        self._check_text(username, 256, "Имя")
        self._check_text(message, 8096, "Сообщение")
        with self.connection:
            self.connection.execute(
                "INSERT INTO comments (id, name, message) VALUES (?, ?, ?)",
                (comment_id, username, message),
            )
        return True

    def update(self, comment_id: int, new_message: str) -> bool:
        self._check_id(comment_id)
        self._check_text(new_message, 8096, "Сообщение")
        with self.connection:
            cursor = self.connection.execute(
                "UPDATE comments SET message = ? WHERE id = ?",
                (new_message, comment_id),
            )
        return cursor.rowcount > 0

    def delete(self, comment_id: int) -> bool:
        self._check_id(comment_id)
        with self.connection:
            cursor = self.connection.execute(
                "DELETE FROM comments WHERE id = ?", (comment_id,)
            )
        return cursor.rowcount > 0

    def close(self):
        self.connection.close()
