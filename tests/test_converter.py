import unittest

from converter import Converter


class ConverterTests(unittest.TestCase):
    def test_large_positive(self):
        for x in (100.7, 100.8, 1000.0, 99999.9):
            with self.subTest(x=x):
                self.assertEqual(Converter.do(x), 1000)

    def test_positive(self):
        cases = [(0.1, 0), (0.9, 0), (1.0, 1), (1.9, 1),
                 (65.7, 65), (100.5, 100), (100.6, 100)]
        for x, expected in cases:
            with self.subTest(x=x):
                self.assertEqual(Converter.do(x), expected)

    def test_zero(self):
        for x in (0.0, -0.0):
            with self.subTest(x=x):
                with self.assertRaises(ValueError):
                    Converter.do(x)

    def test_negative(self):
        cases = [(-0.1, -5), (-0.9, -5), (-1.0, -6), (-1.9, -6),
                 (-15.7, -20), (-30.3, -35), (-30.4, -35)]
        for x, expected in cases:
            with self.subTest(x=x):
                self.assertEqual(Converter.do(x), expected)

    def test_large_negative(self):
        for x in (-30.5, -30.6, -94.5, -1000.0):
            with self.subTest(x=x):
                self.assertEqual(Converter.do(x), -2000)

    def test_result_type(self):
        for x in (100.7, 65.7, -0.1, -30.4, -30.5):
            with self.subTest(x=x):
                self.assertIs(type(Converter.do(x)), int)
