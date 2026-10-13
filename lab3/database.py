"""SQLite хранит результат для каждой тройки введённых сторон."""

from pathlib import Path
import sqlite3


class TriangleDatabase:
    def __init__(self, path: str | Path = ":memory:"):
        # :memory: удобно для тестов: новая БД живёт только в памяти.
        self.connection = sqlite3.connect(path)
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("""
            CREATE TABLE IF NOT EXISTS triangles (
                side_a TEXT NOT NULL,
                side_b TEXT NOT NULL,
                side_c TEXT NOT NULL,
                triangle_type TEXT NOT NULL,
                error_message TEXT NOT NULL,
                PRIMARY KEY (side_a, side_b, side_c)
            )
        """)
        self.connection.commit()

    def add(self, side_a, side_b, side_c, triangle_type, error_message="") -> None:
        # ? — параметры SQL. Введённый текст не превращается в SQL-команды.
        with self.connection:
            self.connection.execute("""
                INSERT INTO triangles VALUES (?, ?, ?, ?, ?)
                ON CONFLICT (side_a, side_b, side_c) DO UPDATE SET
                    triangle_type = excluded.triangle_type,
                    error_message = excluded.error_message
            """, (side_a, side_b, side_c, triangle_type, error_message))

    def get(self, side_a, side_b, side_c) -> dict | None:
        row = self.connection.execute("""
            SELECT * FROM triangles
            WHERE side_a = ? AND side_b = ? AND side_c = ?
        """, (side_a, side_b, side_c)).fetchone()
        # None сообщает контроллеру, что вычисление ещё не сохранено.
        return dict(row) if row is not None else None

    def delete(self, side_a, side_b, side_c) -> bool:
        with self.connection:
            cursor = self.connection.execute("""
                DELETE FROM triangles
                WHERE side_a = ? AND side_b = ? AND side_c = ?
            """, (side_a, side_b, side_c))
        return cursor.rowcount > 0

    def close(self) -> None:
        self.connection.close()
