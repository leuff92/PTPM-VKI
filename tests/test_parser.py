import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import requests

from src.database import DatabaseRepository
from src.parser import ForumParser


ROOT = Path(__file__).resolve().parents[1]


class TestParser(unittest.TestCase):
    def setUp(self):
        self.parser = ForumParser()
        self.html = (ROOT / "data" / "forum.html").read_text(encoding="utf-8")

    def test_parse_fixture(self):
        comments = self.parser.parse_html(self.html)
        self.assertEqual(comments, [
            {"id": 101, "name": "lev", "message": "<p>Изучаю <b>Python</b>.</p>"},
            {"id": 102, "name": "anna", "message": "<p>Данные сохраняются в SQLite.</p>"},
            {"id": 103, "name": "lev", "message": "<p>Тесты проверяют работу программы.</p>"},
        ])

    def test_parse_incomplete_fixture(self):
        html = (ROOT / "tests" / "fixtures" / "invalid_forum.html").read_text(encoding="utf-8")
        self.assertEqual(self.parser.parse_html(html), [
            {"id": 201, "name": "anna", "message": "<p>Полное сообщение.</p>"},
        ])

    def test_parse_empty_page(self):
        self.assertEqual(self.parser.parse_html("<html><body>Нет сообщений</body></html>"), [])

    @patch("src.parser.requests.get")
    def test_parse_page(self, get):
        get.return_value.content = self.html.encode("utf-8")
        self.assertEqual(len(self.parser.parse_page("https://example.com/forum")), 3)
        get.assert_called_once_with(
            "https://example.com/forum",
            headers={"User-Agent": "Lab5ForumParser/1.0"},
            timeout=10,
        )
        get.return_value.raise_for_status.assert_called_once_with()

    @patch("src.parser.requests.get")
    def test_http_error(self, get):
        get.return_value.raise_for_status.side_effect = requests.HTTPError("404")
        with self.assertRaises(requests.HTTPError):
            self.parser.parse_page("https://example.com/missing")

    @patch("src.parser.requests.get", side_effect=requests.Timeout("Нет ответа"))
    def test_timeout(self, get):
        with self.assertRaises(requests.Timeout):
            self.parser.parse_page("https://example.com/forum")

    def test_save_to_db(self):
        repository = DatabaseRepository(":memory:")
        try:
            comments = self.parser.parse_html(self.html)
            self.assertEqual(self.parser.save_to_db(comments, repository), 3)
            self.assertEqual(len(repository.get_by_name("lev")), 2)
            self.assertEqual(repository.get_by_id(102)["name"], "anna")
        finally:
            repository.close()

    def test_save_duplicates(self):
        repository = DatabaseRepository(":memory:")
        try:
            comments = self.parser.parse_html(self.html)
            self.parser.save_to_db(comments, repository)
            self.assertEqual(self.parser.save_to_db(comments, repository), 0)
            self.assertEqual(len(repository.get_by_name("lev")), 2)
        finally:
            repository.close()

    def test_save_empty_data(self):
        repository = Mock()
        self.assertEqual(self.parser.save_to_db([], repository), 0)
        repository.add.assert_not_called()
