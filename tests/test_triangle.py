"""Checks of the public API from lab 1, including numerical regressions."""

import math
import unittest
from unittest.mock import patch

import triangle


class TriangleTests(unittest.TestCase):
    def assert_kind(self, sides, expected):
        kind, points = triangle.classify_triangle(*sides)
        self.assertEqual(kind, expected)
        self.assertEqual(len(points), 3)
        for point in points:
            self.assertIsInstance(point, tuple)
            for coordinate in point:
                self.assertIs(type(coordinate), int)
                self.assertGreaterEqual(coordinate, 0)
                self.assertLessEqual(coordinate, 100)
        return points

    def assert_numeric_error(self, sides):
        with self.assertLogs(triangle.LOGGER, level="ERROR"):
            result = triangle.classify_triangle(*sides)
        self.assertEqual(result, ("не треугольник", [(-1, -1)] * 3))

    def assert_text_error(self, sides):
        with self.assertLogs(triangle.LOGGER, level="ERROR"):
            result = triangle.classify_triangle(*sides)
        self.assertEqual(result, ("", [(-2, -2)] * 3))

    def test_equal_sides_return_equilateral(self):
        self.assert_kind(("5", "5", "5"), "равносторонний")

    def test_equal_a_b_return_isosceles(self):
        self.assert_kind(("5", "5", "6"), "равнобедренный")

    def test_equal_b_c_return_isosceles(self):
        self.assert_kind(("6", "5", "5"), "равнобедренный")

    def test_equal_a_c_return_isosceles(self):
        self.assert_kind(("5", "6", "5"), "равнобедренный")

    def test_three_different_sides_return_scalene(self):
        self.assert_kind(("3", "4", "5"), "разносторонний")

    def test_decimal_sides_are_accepted(self):
        self.assert_kind(("1.5", "2", "2.5"), "разносторонний")

    def test_surrounding_whitespace_is_accepted(self):
        self.assert_kind((" 3 ", "\t4", "5\n"), "разносторонний")

    def test_scientific_notation_is_accepted(self):
        self.assert_kind(("3e2", "4e2", "5e2"), "разносторонний")

    def test_zero_side_is_rejected(self):
        self.assert_numeric_error(("0", "2", "2"))

    def test_negative_side_is_rejected(self):
        self.assert_numeric_error(("2", "-1", "2"))

    def test_degenerate_largest_a_is_rejected(self):
        self.assert_numeric_error(("3", "1", "2"))

    def test_degenerate_largest_b_is_rejected(self):
        self.assert_numeric_error(("1", "3", "2"))

    def test_degenerate_largest_c_is_rejected(self):
        self.assert_numeric_error(("1", "2", "3"))

    def test_sum_below_largest_side_is_rejected(self):
        self.assert_numeric_error(("1", "2", "4"))

    def test_value_just_inside_triangle_boundary_is_accepted(self):
        self.assert_kind(("1", "1", "1.9999999999999998"), "равнобедренный")

    def test_value_just_outside_triangle_boundary_is_rejected(self):
        self.assert_numeric_error(("1", "1", "2.0000000000000004"))

    def test_letter_in_first_side_returns_text_error(self):
        self.assert_text_error(("abc", "4", "5"))

    def test_empty_second_side_returns_text_error(self):
        self.assert_text_error(("3", "", "5"))

    def test_letter_in_third_side_returns_text_error(self):
        self.assert_text_error(("3", "4", "abc"))

    def test_decimal_comma_returns_text_error(self):
        self.assert_text_error(("3,5", "4", "5"))

    def test_none_returns_text_error(self):
        self.assert_text_error((None, "4", "5"))

    def test_nan_returns_numeric_error(self):
        self.assert_numeric_error(("nan", "4", "5"))

    def test_positive_infinity_returns_numeric_error(self):
        self.assert_numeric_error(("3", "inf", "5"))

    def test_negative_infinity_returns_numeric_error(self):
        self.assert_numeric_error(("3", "4", "-inf"))

    def test_float_overflow_returns_numeric_error(self):
        self.assert_numeric_error(("1e309", "4", "5"))

    def test_tiny_scalene_sides_stay_scalene(self):
        self.assert_kind(("3e-15", "4e-15", "5e-15"), "разносторонний")

    def test_tiny_isosceles_sides_stay_isosceles(self):
        self.assert_kind(("5e-15", "5e-15", "6e-15"), "равнобедренный")

    def test_close_but_distinct_sides_stay_scalene(self):
        self.assert_kind(("1", "1.0000000001", "1.0000000002"), "разносторонний")

    def test_very_large_sides_do_not_overflow_geometry(self):
        self.assert_kind(("1e308", "1e308", "1e308"), "равносторонний")

    def test_subnormal_sides_keep_their_type(self):
        self.assert_kind(("3e-320", "4e-320", "5e-320"), "разносторонний")

    def test_short_base_is_not_lost_in_triangle_inequality(self):
        self.assert_kind(("1e-300", "1", "1"), "равнобедренный")

    def test_extreme_ratio_does_not_divide_by_zero(self):
        self.assert_kind(("1e-300", "1e300", "1e300"), "равнобедренный")

    def test_vertices_preserve_side_ratios_after_rounding(self):
        for sides in ((3, 4, 5), (5, 3, 4), (4, 5, 3)):
            with self.subTest(sides=sides):
                points = self.assert_kind(tuple(map(str, sides)), "разносторонний")
                lengths = [math.dist(points[i], points[(i + 1) % 3]) for i in range(3)]
                scale = max(lengths) / 5
                for actual, expected in zip(lengths, sides):
                    self.assertAlmostEqual(actual, expected * scale, delta=1.5)

    def test_scaling_input_does_not_change_pixel_coordinates(self):
        small = triangle.classify_triangle("3", "4", "5")
        large = triangle.classify_triangle("3e100", "4e100", "5e100")
        self.assertEqual(small, large)

    def test_equilateral_vertices_have_nonzero_area(self):
        p, q, r = self.assert_kind(("7", "7", "7"), "равносторонний")
        area2 = (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0])
        self.assertNotEqual(area2, 0)

    def test_obtuse_triangle_fits_canvas(self):
        self.assert_kind(("3", "6", "4"), "разносторонний")

    def test_error_coordinate_lists_are_independent(self):
        with self.assertLogs(triangle.LOGGER, level="ERROR"):
            first = triangle.classify_triangle("0", "2", "2")[1]
            first[0] = (99, 99)
            second = triangle.classify_triangle("0", "2", "2")[1]
        self.assertEqual(second, [(-1, -1)] * 3)

    def test_success_log_contains_input_and_result(self):
        with self.assertLogs(triangle.LOGGER, level="INFO") as captured:
            triangle.classify_triangle("3", "4", "5")
        message = "\n".join(captured.output)
        self.assertIn("a=3", message)
        self.assertIn("разносторонний", message)
        self.assertIn("координаты", message)

    def test_unexpected_geometry_error_records_traceback(self):
        with patch.object(triangle, "_calculate_coordinates", side_effect=RuntimeError("test failure")):
            with self.assertLogs(triangle.LOGGER, level="ERROR") as captured:
                result = triangle.classify_triangle("3", "4", "5")
        self.assertEqual(result, ("не треугольник", [(-1, -1)] * 3))
        self.assertIsNotNone(captured.records[0].exc_info)
        self.assertIn("Traceback", "\n".join(captured.output))


if __name__ == "__main__":
    unittest.main()
