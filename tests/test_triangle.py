"""Unit tests for the triangle laboratory work."""

import unittest

from triangle import classify_triangle


class ClassifyTriangleTests(unittest.TestCase):
    def test_equilateral_triangle(self) -> None:
        kind, coordinates = classify_triangle("5", "5", "5")

        self.assertEqual(kind, "равносторонний")
        self._assert_coordinates_on_canvas(coordinates)

    def test_isosceles_triangle(self) -> None:
        kind, coordinates = classify_triangle("5", "5", "6")

        self.assertEqual(kind, "равнобедренный")
        self._assert_coordinates_on_canvas(coordinates)

    def test_scalene_triangle(self) -> None:
        kind, coordinates = classify_triangle("3", "4", "5")

        self.assertEqual(kind, "разносторонний")
        self._assert_coordinates_on_canvas(coordinates)

    def test_invalid_numeric_values_return_minus_one_coordinates(self) -> None:
        self.assertEqual(
            classify_triangle("1", "2", "3"),
            ("не треугольник", [(-1, -1), (-1, -1), (-1, -1)]),
        )
        self.assertEqual(
            classify_triangle("0", "2", "2"),
            ("не треугольник", [(-1, -1), (-1, -1), (-1, -1)]),
        )

    def test_non_numeric_values_return_minus_two_coordinates(self) -> None:
        self.assertEqual(
            classify_triangle("a", "2", "2"),
            ("", [(-2, -2), (-2, -2), (-2, -2)]),
        )

    def test_nan_and_infinity_are_invalid_numeric_values(self) -> None:
        for value in ("nan", "inf", "-inf"):
            with self.subTest(value=value):
                self.assertEqual(
                    classify_triangle(value, "2", "2"),
                    ("не треугольник", [(-1, -1), (-1, -1), (-1, -1)]),
                )

    def _assert_coordinates_on_canvas(
        self, coordinates: list[tuple[int, int]]
    ) -> None:
        self.assertEqual(len(coordinates), 3)
        self.assertEqual(len(set(coordinates)), 3)
        for x, y in coordinates:
            self.assertIsInstance(x, int)
            self.assertIsInstance(y, int)
            self.assertGreaterEqual(x, 0)
            self.assertLessEqual(x, 100)
            self.assertGreaterEqual(y, 0)
            self.assertLessEqual(y, 100)


if __name__ == "__main__":
    unittest.main()
