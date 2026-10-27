from converter import Converter


def main() -> None:
    try:
        x = float(input("Введите x с одним знаком после точки: "))
        print("Результат:", Converter.do(x))
    except ValueError as error:
        print("Ошибка:", error)


if __name__ == "__main__":
    main()
