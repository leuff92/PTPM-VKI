"""Необязательный консольный запуск для демонстрации Converter."""

from converter import Converter


def main() -> None:
    """Прочитать одно число и показать результат или ошибку."""
    try:
        x = float(input("Введите x с одним знаком после точки: "))
        print("Результат:", Converter.do(x))
    except ValueError as error:
        # Обрабатываем ноль и текст, который невозможно перевести в float.
        print("Ошибка:", error)


if __name__ == "__main__":
    main()
