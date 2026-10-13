"""Класс вычислений использует метод проекта из первой лабораторной."""

from triangle import classify_triangle


class TriangleCalculator:
    def calculate(self, side_a: str, side_b: str, side_c: str):
        # Формула не переписывается: используем исправленный код из ЛР1/ЛР2.
        return classify_triangle(side_a, side_b, side_c)
