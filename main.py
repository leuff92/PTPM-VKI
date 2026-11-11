import argparse
from decimal import InvalidOperation
from pathlib import Path

import requests

from src.parser import collect_products, save_csv


def main() -> None:
    arguments = argparse.ArgumentParser(description="Выгрузка каталога Books to Scrape")
    arguments.add_argument("--pages", type=int, default=2, help="Сколько страниц скачать")
    options = arguments.parse_args()
    if options.pages < 1:
        arguments.error("--pages должно быть не меньше 1")

    output = Path(__file__).with_name("products.csv")
    try:
        products = collect_products(options.pages)
        save_csv(products, output)
    except (requests.RequestException, OSError, ValueError, InvalidOperation) as error:
        arguments.exit(1, f"Ошибка выгрузки: {error}\n")

    for product in products[:5]:
        print(f"{product.title} — {product.price:.2f} GBP")
    print(f"Выгружено товаров: {len(products)}")
    print(f"Файл: {output.resolve()}")


if __name__ == "__main__":
    main()
