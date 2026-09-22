"""Business logic for laboratory work No. 1 (triangle classification)."""

from __future__ import annotations

import logging
import math
from typing import Final


LOGGER = logging.getLogger(__name__)
CANVAS_SIZE: Final[int] = 100
NUMERIC_ERROR_COORDINATES: Final[list[tuple[int, int]]] = [(-1, -1)] * 3
TEXT_ERROR_COORDINATES: Final[list[tuple[int, int]]] = [(-2, -2)] * 3


def classify_triangle(
    side_a: str, side_b: str, side_c: str
) -> tuple[str, list[tuple[int, int]]]:
    """Return a triangle kind and coordinates for three string side lengths.

    The side convention is ``AB = a``, ``BC = b`` and ``CA = c``.  Valid
    coordinates are scaled to the 100 x 100 canvas.  A non-numeric input is
    distinguished from an invalid numeric input, as required by the task.
    """

    raw_sides = (side_a, side_b, side_c)
    try:
        sides = tuple(float(value) for value in raw_sides)
    except (TypeError, ValueError):
        LOGGER.error(
            "Некорректные нечисловые входные данные: a=%r, b=%r, c=%r",
            side_a,
            side_b,
            side_c,
        )
        return "", TEXT_ERROR_COORDINATES.copy()

    if not _forms_triangle(sides):
        LOGGER.error(
            "Числовые данные не образуют треугольник: a=%s, b=%s, c=%s",
            side_a,
            side_b,
            side_c,
        )
        return "не треугольник", NUMERIC_ERROR_COORDINATES.copy()

    try:
        triangle_kind = _triangle_kind(sides)
        coordinates = _calculate_coordinates(sides)
    except Exception:
        # Unexpected errors must include the complete traceback in the log.
        LOGGER.exception(
            "Сбой вычисления треугольника: a=%s, b=%s, c=%s",
            side_a,
            side_b,
            side_c,
        )
        return "не треугольник", NUMERIC_ERROR_COORDINATES.copy()

    LOGGER.info(
        "Успешный запрос: a=%s, b=%s, c=%s; тип=%s; координаты=%s",
        side_a,
        side_b,
        side_c,
        triangle_kind,
        coordinates,
    )
    return triangle_kind, coordinates


def _forms_triangle(sides: tuple[float, float, float]) -> bool:
    """Validate finiteness, positivity and the strict triangle inequality."""

    if not all(math.isfinite(side) and side > 0 for side in sides):
        return False
    smallest, middle, largest = sorted(sides)
    # Adding a tiny side to a large one may round back to the large value.
    # Subtract the two larger sides instead; this also avoids sum overflow.
    return smallest > largest - middle


def _triangle_kind(sides: tuple[float, float, float]) -> str:
    """Classify the actual float values, without changing unequal side lengths."""

    a, b, c = sides
    if a == b == c:
        return "равносторонний"
    if a == b or b == c or a == c:
        return "равнобедренный"
    return "разносторонний"


def _calculate_coordinates(sides: tuple[float, float, float]) -> list[tuple[int, int]]:
    """Calculate integer vertex coordinates that fit into a 100 x 100 field."""

    # Use the longest side as a unit base so it cannot underflow to zero.
    base_index = max(range(3), key=sides.__getitem__)
    largest = sides[base_index]
    previous_side = sides[(base_index + 2) % 3] / largest
    next_side = sides[(base_index + 1) % 3] / largest
    third_x = (1.0 + (previous_side - next_side) * (previous_side + next_side)) / 2

    # Stable rearrangement of Heron's formula: height = 2 * area / base.
    middle, smallest = sorted((previous_side, next_side), reverse=True)
    factors = (1 + (middle + smallest), smallest - (1 - middle),
               smallest + (1 - middle), 1 + (middle - smallest))
    third_y = math.prod(math.sqrt(max(0.0, factor)) for factor in factors) / 2

    scale = CANVAS_SIZE
    offset_x = 0.0
    offset_y = (CANVAS_SIZE - third_y * scale) / 2
    points = [(0.0, 0.0)] * 3
    points[base_index] = (0.0, 0.0)
    points[(base_index + 1) % 3] = (1.0, 0.0)
    points[(base_index + 2) % 3] = (third_x, third_y)

    return [
        (
            _canvas_coordinate(offset_x + x * scale),
            _canvas_coordinate(offset_y + y * scale),
        )
        for x, y in points
    ]


def _canvas_coordinate(value: float) -> int:
    """Round a coordinate and protect against floating-point edge effects."""

    return max(0, min(CANVAS_SIZE, round(round(value, 10))))
