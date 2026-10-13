"""Запускайте этот файл в PyCharm или командой python main.py."""

import logging
from pathlib import Path

from calculator import TriangleCalculator
from controller import Controller
from database import TriangleDatabase
from sender import SimulatedSender
from user_input import ConsoleInput

DATABASE_PATH = Path(__file__).resolve().parent / "data" / "triangles.sqlite3"


def main(database_path=DATABASE_PATH) -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    Path(database_path).parent.mkdir(parents=True, exist_ok=True)
    database = TriangleDatabase(database_path)
    try:
        # Здесь собираем четыре независимых компонента в один контроллер.
        controller = Controller(
            ConsoleInput(), TriangleCalculator(), database, SimulatedSender()
        )
        print("Результат:", controller.run())
    finally:
        # Закрываем БД даже при ошибке ввода или отправки.
        database.close()


if __name__ == "__main__":
    main()
