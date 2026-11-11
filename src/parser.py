import csv
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

CATALOG_URL = "https://books.toscrape.com/"


@dataclass(frozen=True)
class Product:
    title: str
    price: Decimal
    availability: str
    url: str


def parse_page(html: str, page_url: str) -> tuple[list[Product], str | None]:
    """Извлекает товары и ссылку на следующую страницу каталога."""
    soup = BeautifulSoup(html, "html.parser")
    cards = soup.select("article.product_pod")
    if not cards:
        raise ValueError(f"На странице нет карточек товаров: {page_url}")

    products = []
    for card in cards:
        title_link = card.select_one("h3 a[title][href]")
        price = card.select_one("p.price_color")
        availability = card.select_one("p.availability")
        if title_link is None or price is None or availability is None:
            raise ValueError(f"В карточке товара отсутствуют данные: {page_url}")

        price_text = price.get_text(strip=True)
        if not price_text.startswith("£"):
            raise ValueError(f"Неожиданный формат цены: {price_text}")

        products.append(
            Product(
                title=title_link["title"],
                price=Decimal(price_text.removeprefix("£")),
                availability=availability.get_text(strip=True),
                url=urljoin(page_url, title_link["href"]),
            )
        )

    next_link = soup.select_one("li.next a[href]")
    next_url = urljoin(page_url, next_link["href"]) if next_link else None
    return products, next_url


def collect_products(max_pages: int = 2) -> list[Product]:
    """Загружает указанное количество страниц, если они есть на сайте."""
    products = []
    page_url = CATALOG_URL
    with requests.Session() as session:
        for _ in range(max_pages):
            response = session.get(page_url, timeout=20)
            response.raise_for_status()
            page_products, next_url = parse_page(response.content.decode("utf-8"), response.url)
            products.extend(page_products)
            if next_url is None:
                break
            page_url = next_url
    return products


def save_csv(products: list[Product], output: Path) -> None:
    """Записывает товары в CSV с настройками для русской версии Excel."""
    with output.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.writer(file, delimiter=";")
        writer.writerow(["Название", "Цена", "Валюта", "Наличие", "Ссылка"])
        for product in products:
            price = format(product.price, ".2f").replace(".", ",")
            writer.writerow([product.title, price, "GBP", product.availability, product.url])
