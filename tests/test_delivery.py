"""Delivery tests against the unchanged teacher's module.

The reconstructed contract and assumptions are in LAB2_RESULTS.md.
Failing assertions are deliberately visible, never skipped or expectedFailure.
"""

import unittest

from Delivery import calculate_delivery_cost as calculate


class DeliveryTests(unittest.TestCase):
    def test_minimum_weight_is_accepted(self):
        self.assertEqual(calculate(0.1, 100, "обычный"), (700, "2026-09-04"))

    def test_maximum_weight_is_accepted(self):
        self.assertEqual(calculate(50, 100, "обычный"), (1050, "2026-09-04"))

    def test_minimum_distance_is_accepted(self):
        self.assertEqual(calculate(1, 1, "обычный"), (205, "2026-09-04"))

    def test_maximum_distance_is_accepted(self):
        self.assertEqual(calculate(1, 5000, "обычный"), (25200, "2026-09-13"))

    def test_weight_below_minimum_is_rejected(self):
        self.assertEqual(calculate(0.09, 100, "обычный"), (-1, "0000-00-00"))

    def test_weight_above_maximum_is_rejected(self):
        self.assertEqual(calculate(50.01, 100, "обычный"), (-1, "0000-00-00"))

    def test_zero_weight_is_rejected(self):
        self.assertEqual(calculate(0, 100, "обычный"), (-1, "0000-00-00"))

    def test_negative_weight_is_rejected(self):
        self.assertEqual(calculate(-1, 100, "обычный"), (-1, "0000-00-00"))

    def test_zero_distance_is_rejected(self):
        self.assertEqual(calculate(1, 0, "обычный"), (-1, "0000-00-00"))

    def test_distance_above_maximum_is_rejected(self):
        self.assertEqual(calculate(1, 5001, "обычный"), (-1, "0000-00-00"))

    def test_unknown_package_type_is_rejected(self):
        self.assertEqual(calculate(1, 100, "письмо"), (-1, "0000-00-00"))

    def test_weight_just_below_five_has_no_surcharge(self):
        self.assertEqual(calculate(4.999, 100, "обычный")[0], 700)

    def test_weight_exactly_five_has_no_surcharge(self):
        self.assertEqual(calculate(5, 100, "обычный")[0], 700)

    def test_weight_just_above_five_adds_twenty_percent(self):
        self.assertEqual(calculate(5.001, 100, "обычный")[0], 840)

    def test_weight_just_below_twenty_adds_twenty_percent(self):
        self.assertEqual(calculate(19.999, 100, "обычный")[0], 840)

    def test_weight_exactly_twenty_adds_fifty_percent(self):
        self.assertEqual(calculate(20, 100, "обычный")[0], 1050)

    def test_fragile_package_adds_three_hundred(self):
        self.assertEqual(calculate(1, 100, "хрупкий")[0], 1000)

    def test_dangerous_package_adds_one_thousand(self):
        self.assertEqual(calculate(1, 100, "опасный")[0], 1700)

    def test_fragile_surcharge_is_added_after_weight_multiplier(self):
        self.assertEqual(calculate(20, 100, "хрупкий")[0], 1350)

    def test_dangerous_surcharge_is_added_after_weight_multiplier(self):
        self.assertEqual(calculate(10, 100, "опасный")[0], 1840)

    def test_default_delivery_equals_explicit_non_express(self):
        self.assertEqual(calculate(1, 500, "обычный"), calculate(1, 500, "обычный", False))

    def test_five_hundred_kilometres_take_one_day(self):
        self.assertEqual(calculate(1, 500, "обычный")[1], "2026-09-04")

    def test_one_thousand_kilometres_take_two_days(self):
        self.assertEqual(calculate(1, 1000, "обычный")[1], "2026-09-05")

    def test_infinite_weight_is_rejected(self):
        self.assertEqual(calculate(float("inf"), 100, "обычный"), (-1, "0000-00-00"))

    def test_infinite_distance_is_rejected(self):
        self.assertEqual(calculate(1, float("inf"), "обычный"), (-1, "0000-00-00"))

    # Inferred rule: a partially travelled 500 km interval needs a whole day.
    def test_501_kilometres_require_two_days(self):
        self.assertEqual(calculate(1, 501, "обычный")[1], "2026-09-05")

    def test_999_kilometres_require_two_days(self):
        self.assertEqual(calculate(1, 999, "обычный")[1], "2026-09-05")

    def test_1001_kilometres_require_three_days(self):
        self.assertEqual(calculate(1, 1001, "обычный")[1], "2026-09-06")

    def test_4999_kilometres_require_ten_days(self):
        self.assertEqual(calculate(1, 4999, "обычный")[1], "2026-09-13")

    # Inferred rule: express is an extra service, not a discount.
    def test_express_cost_exceeds_regular_cost(self):
        self.assertGreater(calculate(1, 1000, "обычный", True)[0], calculate(1, 1000, "обычный")[0])

    def test_express_fragile_cost_exceeds_regular_cost(self):
        self.assertGreater(calculate(10, 1000, "хрупкий", True)[0], calculate(10, 1000, "хрупкий")[0])

    # Inferred rule: halve the duration, round up, never deliver in zero days.
    def test_short_express_delivery_takes_at_least_one_day(self):
        self.assertEqual(calculate(1, 1, "обычный", True)[1], "2026-09-04")

    def test_500_kilometre_express_delivery_takes_one_day(self):
        self.assertEqual(calculate(1, 500, "обычный", True)[1], "2026-09-04")

    def test_three_day_express_route_rounds_up_to_two_days(self):
        self.assertEqual(calculate(1, 1500, "обычный", True)[1], "2026-09-05")

    def test_five_day_express_route_rounds_up_to_three_days(self):
        self.assertEqual(calculate(1, 2500, "обычный", True)[1], "2026-09-06")

    def test_nan_weight_is_rejected(self):
        self.assertEqual(calculate(float("nan"), 100, "обычный"), (-1, "0000-00-00"))

    def test_nan_distance_is_rejected_without_exception(self):
        self.assertEqual(calculate(1, float("nan"), "обычный"), (-1, "0000-00-00"))

    def test_string_weight_is_rejected_without_exception(self):
        self.assertEqual(calculate("1", 100, "обычный"), (-1, "0000-00-00"))

    def test_string_distance_is_rejected_without_exception(self):
        self.assertEqual(calculate(1, "100", "обычный"), (-1, "0000-00-00"))

    def test_none_weight_is_rejected_without_exception(self):
        self.assertEqual(calculate(None, 100, "обычный"), (-1, "0000-00-00"))

    def test_fractional_distance_is_rejected(self):
        self.assertEqual(calculate(1, 100.5, "обычный"), (-1, "0000-00-00"))

    def test_boolean_weight_is_rejected(self):
        self.assertEqual(calculate(True, 100, "обычный"), (-1, "0000-00-00"))

    def test_boolean_distance_is_rejected(self):
        self.assertEqual(calculate(1, True, "обычный"), (-1, "0000-00-00"))

    def test_string_express_flag_is_rejected(self):
        self.assertEqual(calculate(1, 100, "обычный", "False"), (-1, "0000-00-00"))


if __name__ == "__main__":
    unittest.main()
