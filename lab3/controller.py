"""Главный сценарий: ввод → поиск в БД → вычисление → сохранение → отправка."""

import logging

from calculator import TriangleCalculator
from database import TriangleDatabase
from interfaces import ResultSender, UserInput

LOGGER = logging.getLogger(__name__)


class Controller:
    def __init__(self, user_input: UserInput, calculator: TriangleCalculator,
                 database: TriangleDatabase, sender: ResultSender):
        # Передаём зависимости снаружи: в тестах их удобно заменять заглушками.
        self.user_input = user_input
        self.calculator = calculator
        self.database = database
        self.sender = sender

    def run(self) -> str:
        # 1. Получить стороны. Звёздочка * разворачивает кортеж в три аргумента.
        sides = self.user_input.get_sides()

        # 2. Проверить кэш. Ключ БД — три введённые строки в заданном порядке.
        record = self.database.get(*sides)
        if record is None:
            LOGGER.info("Записи нет: вычисляем результат и сохраняем в SQLite.")
            triangle_type, _coordinates = self.calculator.calculate(*sides)
            if triangle_type == "":
                error_message = "Стороны должны быть вещественными числами."
            elif triangle_type == "не треугольник":
                error_message = "Стороны не образуют треугольник."
            else:
                error_message = ""

            self.database.add(*sides, triangle_type, error_message)
            record = {"triangle_type": triangle_type, "error_message": error_message}
        else:
            LOGGER.info("Запись найдена: берём готовый результат из SQLite.")

        # 3. Отправляем одну и ту же строку для нового и сохранённого результата.
        if record["error_message"]:
            message = f"Ошибка: {record['error_message']}"
        else:
            message = record["triangle_type"]
        self.sender.send_result(message)

        # 4. Возвращаем результат, чтобы его показал main.py или проверил тест.
        return message
