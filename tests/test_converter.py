"""Все пять диапазонов, соседние с границами значения и исключение для нуля."""

import unittest

from converter import Converter


class ConverterTests(unittest.TestCase):
    def test_large_positive_values_return_1000(self):
        for x in (100.7, 100.8, 1000.0, 99999.9):
            with self.subTest(x=x):
                self.assertEqual(Converter.do(x), 1000)

    def test_positive_values_below_boundary_are_truncated(self):
        cases = [(0.1, 0), (0.9, 0), (1.0, 1), (1.9, 1),
                 (65.7, 65), (100.5, 100), (100.6, 100)]
        for x, expected in cases:
            with self.subTest(x=x):
                self.assertEqual(Converter.do(x), expected)

    def test_zero_raises_value_error(self):
        for x in (0.0, -0.0):
            with self.subTest(x=x):
                # Проверяем исключение, а не возврат строки или числа.
                with self.assertRaises(ValueError):
                    Converter.do(x)

    def test_negative_values_near_zero_are_truncated_minus_five(self):
        cases = [(-0.1, -5), (-0.9, -5), (-1.0, -6), (-1.9, -6),
                 (-15.7, -20), (-30.3, -35), (-30.4, -35)]
        for x, expected in cases:
            with self.subTest(x=x):
                self.assertEqual(Converter.do(x), expected)

    def test_values_at_or_below_negative_boundary_return_minus_2000(self):
        for x in (-30.5, -30.6, -94.5, -1000.0):
            with self.subTest(x=x):
                self.assertEqual(Converter.do(x), -2000)

    def test_result_type_is_exactly_int(self):
        for x in (100.7, 65.7, -0.1, -30.4, -30.5):
            with self.subTest(x=x):
                # Проверяем тип результата отдельно от его значения.
                self.assertIs(type(Converter.do(x)), int)
