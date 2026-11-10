import sqlite3
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from src.database import DatabaseRepository


class TestDatabase(unittest.TestCase):
    def setUp(self):
        self.repository = DatabaseRepository(":memory:")

    def tearDown(self):
        self.repository.close()

    def test_add(self):
        self.assertTrue(self.repository.add(1, "lev", "<b>Привет</b>"))
        self.assertEqual(
            self.repository.get_by_id(1),
            {"id": 1, "name": "lev", "message": "<b>Привет</b>"},
        )

    def test_add_duplicate(self):
        self.repository.add(1, "lev", "Первое")
        with self.assertRaises(sqlite3.IntegrityError):
            self.repository.add(1, "anna", "Второе")
        self.assertEqual(self.repository.get_by_id(1)["message"], "Первое")

    def test_add_limits(self):
        self.assertTrue(self.repository.add(1, "я" * 256, "т" * 8096))
        self.assertEqual(len(self.repository.get_by_id(1)["message"]), 8096)

    def test_add_long_name(self):
        with self.assertRaises(ValueError):
            self.repository.add(1, "я" * 257, "Текст")
        self.assertIsNone(self.repository.get_by_id(1))

    def test_add_long_message(self):
        with self.assertRaises(ValueError):
            self.repository.add(1, "lev", "т" * 8097)

    def test_add_invalid_types(self):
        for values in [("1", "lev", "Текст"), (True, "lev", "Текст"),
                       (1.0, "lev", "Текст"), (1, None, "Текст"),
                       (1, 123, "Текст"), (1, "lev", None), (1, "lev", 123)]:
            with self.subTest(values=values):
                with self.assertRaises(TypeError):
                    self.repository.add(*values)

    def test_add_empty_strings(self):
        self.assertTrue(self.repository.add(1, "", ""))

    def test_get_by_id(self):
        self.repository.add(2, "anna", "Текст")
        self.assertEqual(self.repository.get_by_id(2)["name"], "anna")

    def test_get_by_id_missing(self):
        self.assertIsNone(self.repository.get_by_id(999))

    def test_get_by_id_invalid_type(self):
        with self.assertRaises(TypeError):
            self.repository.get_by_id("1")

    def test_get_by_name(self):
        self.repository.add(3, "lev", "Третье")
        self.repository.add(1, "lev", "Первое")
        self.repository.add(2, "anna", "Второе")
        self.assertEqual([row["id"] for row in self.repository.get_by_name("lev")], [1, 3])

    def test_get_by_name_missing(self):
        self.assertEqual(self.repository.get_by_name("unknown"), [])

    def test_get_by_name_invalid_type(self):
        with self.assertRaises(TypeError):
            self.repository.get_by_name(None)

    def test_update(self):
        self.repository.add(1, "lev", "Старое")
        self.assertTrue(self.repository.update(1, "<p>Новое</p>"))
        self.assertEqual(self.repository.get_by_id(1)["message"], "<p>Новое</p>")

    def test_update_missing(self):
        self.assertFalse(self.repository.update(999, "Новое"))

    def test_update_long_message(self):
        self.repository.add(1, "lev", "Старое")
        with self.assertRaises(ValueError):
            self.repository.update(1, "т" * 8097)
        self.assertEqual(self.repository.get_by_id(1)["message"], "Старое")

    def test_update_invalid_types(self):
        for comment_id, message in [("1", "Текст"), (1, None)]:
            with self.subTest(comment_id=comment_id, message=message):
                with self.assertRaises(TypeError):
                    self.repository.update(comment_id, message)

    def test_update_limit(self):
        self.repository.add(1, "lev", "Старое")
        self.assertTrue(self.repository.update(1, "т" * 8096))

    def test_delete(self):
        self.repository.add(1, "lev", "Текст")
        self.assertTrue(self.repository.delete(1))
        self.assertIsNone(self.repository.get_by_id(1))

    def test_delete_missing(self):
        self.assertFalse(self.repository.delete(999))

    def test_delete_invalid_type(self):
        with self.assertRaises(TypeError):
            self.repository.delete(True)

    def test_sql_parameters(self):
        username = "lev'; DROP TABLE comments; --"
        self.repository.add(1, username, "Текст")
        self.assertEqual(len(self.repository.get_by_name(username)), 1)
        self.assertEqual(self.repository.get_by_name("anna' OR 1=1 --"), [])
        self.assertEqual(self.repository.get_by_id(1)["name"], username)

    def test_file_persistence(self):
        with TemporaryDirectory() as folder:
            path = str(Path(folder) / "comments.db")
            repository = DatabaseRepository(path)
            try:
                repository.add(1, "lev", "Сохранено")
            finally:
                repository.close()
            repository = DatabaseRepository(path)
            try:
                self.assertEqual(repository.get_by_id(1)["message"], "Сохранено")
            finally:
                repository.close()
