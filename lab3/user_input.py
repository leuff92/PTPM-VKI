"""Реализация ввода через консоль."""

from interfaces import UserInput


class ConsoleInput(UserInput):
    def get_sides(self) -> tuple[str, str, str]:
        # input() возвращает строки. Проверкой чисел занимается калькулятор.
        side_a = input("Введите сторону A: ").strip()
        side_b = input("Введите сторону B: ").strip()
        side_c = input("Введите сторону C: ").strip()
        return side_a, side_b, side_c
