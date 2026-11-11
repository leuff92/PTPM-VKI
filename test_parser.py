import csv
from decimal import Decimal
from unittest.mock import Mock

import pytest

from src.parser import CATALOG_URL, Product, collect_products, parse_page, save_csv


PRODUCT_HTML = """
<article class="product_pod">
  <h3><a href="book/index.html" title="A Complete Book Title">A Complete...</a></h3>
  <p class="price_color">£51.77</p>
  <p class="instock availability">In stock</p>
</article>
"""
NEXT_LINK = '<li class="next"><a href="catalogue/page-2.html">next</a></li>'


def test_extracts_full_title_price_and_links():
    products, next_url = parse_page(PRODUCT_HTML + NEXT_LINK, CATALOG_URL)

    assert products == [
        Product("A Complete Book Title", Decimal("51.77"), "In stock", CATALOG_URL + "book/index.html")
    ]
    assert next_url == CATALOG_URL + "catalogue/page-2.html"


def test_rejects_page_without_products():
    with pytest.raises(ValueError, match="нет карточек"):
        parse_page("<html>Empty</html>", CATALOG_URL)


def test_downloads_next_page_and_stops_when_catalog_ends(monkeypatch):
    second_page = CATALOG_URL + "catalogue/page-2.html"
    request = Mock(side_effect=[
        Mock(content=(PRODUCT_HTML + NEXT_LINK).encode(), url=CATALOG_URL),
        Mock(content=PRODUCT_HTML.encode(), url=second_page),
    ])
    monkeypatch.setattr("src.parser.requests.Session.get", request)

    products = collect_products(max_pages=5)

    assert len(products) == 2
    assert [call.args[0] for call in request.call_args_list] == [CATALOG_URL, second_page]
    assert products[1].url == CATALOG_URL + "catalogue/book/index.html"


def test_saves_csv_with_full_title_and_price(tmp_path):
    path = tmp_path / "products.csv"
    products = [Product('Книга; "Тест"', Decimal("5.20"), "In stock", CATALOG_URL)]

    save_csv(products, path)

    with path.open(encoding="utf-8-sig", newline="") as file:
        rows = list(csv.reader(file, delimiter=";"))
    assert rows == [
        ["Название", "Цена", "Валюта", "Наличие", "Ссылка"],
        ['Книга; "Тест"', "5,20", "GBP", "In stock", CATALOG_URL],
    ]
