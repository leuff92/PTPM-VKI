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

    a, b, c = sides
    if not all(math.isfinite(side) and side > 0 for side in sides):
        return False
    return a + b > c and a + c > b and b + c > a


def _triangle_kind(sides: tuple[float, float, float]) -> str:
    """Classify a valid triangle using a small tolerance for float input."""

    a, b, c = sides
    ab_equal = math.isclose(a, b, rel_tol=1e-9, abs_tol=1e-12)
    bc_equal = math.isclose(b, c, rel_tol=1e-9, abs_tol=1e-12)
    ac_equal = math.isclose(a, c, rel_tol=1e-9, abs_tol=1e-12)

    if ab_equal and bc_equal:
        return "равносторонний"
    if ab_equal or bc_equal or ac_equal:
        return "равнобедренный"
    return "разносторонний"


def _calculate_coordinates(sides: tuple[float, float, float]) -> list[tuple[int, int]]:
    """Calculate integer vertex coordinates that fit into a 100 x 100 field."""

    a, b, c = sides
    largest_side = max(sides)
    # Normalisation prevents overflow for very large but valid float values.
    base = a / largest_side
    next_side = b / largest_side
    previous_side = c / largest_side

    third_x = (previous_side**2 + base**2 - next_side**2) / (2 * base)
    third_y = math.sqrt(max(0.0, previous_side**2 - third_x**2))

    drawing_width = max(base, third_x) - min(0.0, third_x)
    drawing_height = third_y
    scale = min(
        CANVAS_SIZE / drawing_width,
        CANVAS_SIZE / drawing_height if drawing_height else CANVAS_SIZE,
    )

    offset_x = (CANVAS_SIZE - drawing_width * scale) / 2 - min(0.0, third_x) * scale
    offset_y = (CANVAS_SIZE - drawing_height * scale) / 2
    points = ((0.0, 0.0), (base, 0.0), (third_x, third_y))

    return [
        (
            _canvas_coordinate(offset_x + x * scale),
            _canvas_coordinate(offset_y + y * scale),
        )
        for x, y in points
    ]


def _canvas_coordinate(value: float) -> int:
    """Round a coordinate and protect against floating-point edge effects."""

    return max(0, min(CANVAS_SIZE, round(value)))
