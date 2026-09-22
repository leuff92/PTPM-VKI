"""Console entry point for laboratory work No. 1."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

from triangle import classify_triangle


def configure_logging() -> None:
    """Configure simultaneous UTF-8 file and console logging."""

    log_directory = Path(__file__).parent / "logs"
    log_directory.mkdir(exist_ok=True)
    log_format = "%(asctime)s | [%(levelname)-7s] | %(name)s | %(message)s"
    formatter = logging.Formatter(log_format, datefmt="%Y-%m-%d %H:%M:%S")

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.handlers.clear()

    console_handler = logging.StreamHandler(sys.stdout)
    file_handler = logging.FileHandler(log_directory / "file_txt.log", encoding="utf-8")
    for handler in (console_handler, file_handler):
        handler.setFormatter(formatter)
        root_logger.addHandler(handler)

    logging.info("Логгер успешно сконфигурирован")
    logging.info("Приложение запущено")


def main() -> None:
    """Read three side lengths, calculate the result and print it."""

    configure_logging()
    side_a = input("Введите сторону A: ")
    side_b = input("Введите сторону B: ")
    side_c = input("Введите сторону C: ")

    triangle_kind, coordinates = classify_triangle(side_a, side_b, side_c)
    print(f"Тип фигуры: {triangle_kind}")
    print(f"Координаты вершин: {coordinates}")


if __name__ == "__main__":
    main()
