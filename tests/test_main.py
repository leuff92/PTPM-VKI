import io
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import requests

from main import main
from src.database import DatabaseRepository


class TestMain(unittest.TestCase):
    def test_offline_run(self):
        with TemporaryDirectory() as folder:
            path = str(Path(folder) / "comments.db")
            with redirect_stdout(io.StringIO()) as output:
                self.assertEqual(main(["--db", path]), 0)
                self.assertEqual(main(["--db", path]), 0)
            self.assertIn("Добавлено в базу: 3", output.getvalue())
            self.assertIn("Добавлено в базу: 0", output.getvalue())
            repository = DatabaseRepository(path)
            try:
                self.assertEqual(len(repository.get_by_name("lev")), 2)
            finally:
                repository.close()

    @patch("src.parser.requests.get", side_effect=requests.ConnectionError("Нет соединения"))
    def test_network_error(self, get):
        with redirect_stdout(io.StringIO()) as output:
            self.assertEqual(main(["--url", "http://example.com/forum"]), 1)
        self.assertIn("Ошибка:", output.getvalue())

    def test_database_error(self):
        with TemporaryDirectory() as folder:
            path = str(Path(folder) / "missing" / "comments.db")
            with redirect_stdout(io.StringIO()) as output:
                self.assertEqual(main(["--db", path]), 1)
            self.assertIn("Ошибка:", output.getvalue())
