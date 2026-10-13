"""Проверки новых компонентов ЛР3, без повторения математических тестов ЛР2."""

from pathlib import Path
import runpy
import sqlite3
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import call, patch

from calculator import TriangleCalculator
from database import TriangleDatabase
from interfaces import ResultSender, UserInput
import main
from sender import SimulatedSender
from user_input import ConsoleInput


class DatabaseTests(unittest.TestCase):
    def setUp(self):
        self.database = TriangleDatabase()
        self.addCleanup(self.database.close)

    def test_add_and_get_return_all_required_fields(self):
        self.database.add("a", "b", "c", "", "ошибка")
        self.assertEqual(self.database.get("a", "b", "c"), {
            "side_a": "a", "side_b": "b", "side_c": "c",
            "triangle_type": "", "error_message": "ошибка",
        })

    def test_unknown_key_returns_none(self):
        self.assertIsNone(self.database.get("3", "4", "5"))

    def test_adding_existing_key_updates_one_record(self):
        self.database.add("3", "4", "5", "первый")
        self.database.add("3", "4", "5", "второй")
        self.assertEqual(self.database.get("3", "4", "5")["triangle_type"], "второй")
        count = self.database.connection.execute("SELECT COUNT(*) FROM triangles").fetchone()[0]
        self.assertEqual(count, 1)

    def test_delete_removes_only_requested_key(self):
        self.database.add("3", "4", "5", "первый")
        self.database.add("5", "4", "3", "второй")
        self.assertTrue(self.database.delete("3", "4", "5"))
        self.assertIsNone(self.database.get("3", "4", "5"))
        self.assertIsNotNone(self.database.get("5", "4", "3"))

    def test_delete_missing_key_returns_false(self):
        self.assertFalse(self.database.delete("3", "4", "5"))

    def test_sql_like_input_is_stored_as_plain_text(self):
        text = "3'; DROP TABLE triangles; --"
        self.database.add(text, "4", "5", "", "ошибка")
        self.assertEqual(self.database.get(text, "4", "5")["side_a"], text)
        self.assertTrue(self.database.delete(text, "4", "5"))
        self.database.add("3", "4", "5", "работает")
        self.assertIsNotNone(self.database.get("3", "4", "5"))

    def test_close_releases_sqlite_connection(self):
        database = TriangleDatabase()
        database.close()
        with self.assertRaises(sqlite3.ProgrammingError):
            database.get("3", "4", "5")


class ComponentTests(unittest.TestCase):
    def test_abstract_interfaces_cannot_be_instantiated(self):
        for interface in (UserInput, ResultSender):
            with self.subTest(interface=interface):
                with self.assertRaises(TypeError):
                    interface()

    def test_console_input_uses_three_prompts_and_strips_spaces(self):
        with patch("builtins.input", side_effect=[" 3 ", "\t4", "5 "]) as input_stub:
            result = ConsoleInput().get_sides()
        self.assertEqual(result, ("3", "4", "5"))
        self.assertEqual(input_stub.call_args_list, [call("Введите сторону A: "),
                                                   call("Введите сторону B: "),
                                                   call("Введите сторону C: ")])

    def test_simulated_sender_prints_the_given_result(self):
        with patch("builtins.print") as print_stub:
            SimulatedSender().send_result("сохранённый результат")
        print_stub.assert_called_once_with("[Имитация отправки на сервер] сохранённый результат")

    def test_calculator_delegates_to_lab_one_method(self):
        expected = ("результат", [(1, 2)] * 3)
        with patch("calculator.classify_triangle", return_value=expected) as method:
            actual = TriangleCalculator().calculate("a", "b", "c")
        self.assertEqual(actual, expected)
        method.assert_called_once_with("a", "b", "c")


class MainTests(unittest.TestCase):
    def test_main_builds_components_and_prints_result(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "data" / "triangles.sqlite3"
            with patch("builtins.input", side_effect=["3", "4", "5"]):
                with patch("builtins.print") as output, patch("main.logging.basicConfig"):
                    main.main(path)
            self.assertTrue(path.exists())
            output.assert_any_call("Результат:", "разносторонний")
            database = TriangleDatabase(path)
            try:
                self.assertIsNotNone(database.get("3", "4", "5"))
            finally:
                database.close()

    def test_main_closes_database_if_controller_fails(self):
        with TemporaryDirectory() as directory:
            with patch("main.TriangleDatabase") as database_class:
                with patch("main.Controller") as controller_class:
                    controller_class.return_value.run.side_effect = RuntimeError("сбой")
                    with patch("main.logging.basicConfig"), self.assertRaises(RuntimeError):
                        main.main(Path(directory) / "triangles.sqlite3")
            database_class.return_value.close.assert_called_once_with()

    def test_main_file_can_run_as_a_script(self):
        with patch("database.TriangleDatabase") as database_class:
            database_class.return_value.get.return_value = None
            with patch("builtins.input", side_effect=["3", "4", "5"]):
                with patch("builtins.print") as output, patch("pathlib.Path.mkdir"), patch("logging.basicConfig"):
                    runpy.run_path(str(Path(main.__file__)), run_name="__main__")
            output.assert_any_call("Результат:", "разносторонний")
            database_class.return_value.close.assert_called_once_with()
