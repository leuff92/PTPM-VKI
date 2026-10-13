"""Интеграционные тесты: реальные Controller, калькулятор и SQLite.

Заглушки заменяют только пользователя и внешний сервер. Мы проверяем связи
между модулями, а не повторяем математические юнит-тесты второй лабораторной.
"""

from pathlib import Path
import sqlite3
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import call, create_autospec, Mock, patch

from calculator import TriangleCalculator
from controller import Controller
from database import TriangleDatabase
from interfaces import ResultSender, UserInput
from user_input import ConsoleInput


class IntegrationTests(unittest.TestCase):
    def setUp(self):
        # Для каждого теста — отдельная настоящая БД в памяти.
        self.database = TriangleDatabase()
        self.addCleanup(self.database.close)
        self.user = create_autospec(UserInput, instance=True)
        self.user.get_sides.return_value = ("3", "4", "5")
        self.sender = create_autospec(ResultSender, instance=True)
        # wraps не подменяет математику: реальный метод выполняется, вызов считаем.
        self.calculator = Mock(wraps=TriangleCalculator(), spec=TriangleCalculator)
        self.controller = Controller(self.user, self.calculator, self.database, self.sender)

    def test_new_request_calculates_stores_and_sends_result(self):
        result = self.controller.run()
        record = self.database.get("3", "4", "5")
        self.assertEqual(result, "разносторонний")
        self.assertEqual(record, {"side_a": "3", "side_b": "4", "side_c": "5",
                                  "triangle_type": result, "error_message": ""})
        self.user.get_sides.assert_called_once_with()
        self.calculator.calculate.assert_called_once_with("3", "4", "5")
        self.sender.send_result.assert_called_once_with(result)

    def test_cached_request_sends_database_result_without_calculating(self):
        self.database.add("3", "4", "5", "сохранённый результат")
        result = self.controller.run()
        self.assertEqual(result, "сохранённый результат")
        self.calculator.calculate.assert_not_called()
        self.sender.send_result.assert_called_once_with(result)

    def test_second_request_reuses_cache_and_sends_again(self):
        first = self.controller.run()
        second = self.controller.run()
        self.assertEqual(first, second)
        self.calculator.calculate.assert_called_once()
        self.assertEqual(self.sender.send_result.call_args_list, [call(first), call(second)])

    def test_numeric_error_is_saved_and_reused(self):
        self.user.get_sides.return_value = ("1", "2", "3")
        with self.assertLogs("triangle", level="ERROR"):
            first = self.controller.run()
        second = self.controller.run()
        self.assertEqual(first, "Ошибка: Стороны не образуют треугольник.")
        self.assertEqual(first, second)
        self.assertEqual(self.database.get("1", "2", "3")["triangle_type"], "не треугольник")
        self.calculator.calculate.assert_called_once()
        self.assertEqual(self.sender.send_result.call_count, 2)

    def test_text_error_is_saved_and_sent(self):
        self.user.get_sides.return_value = ("текст", "4", "5")
        with self.assertLogs("triangle", level="ERROR"):
            result = self.controller.run()
        record = self.database.get("текст", "4", "5")
        self.assertEqual(record["triangle_type"], "")
        self.assertEqual(record["error_message"], "Стороны должны быть вещественными числами.")
        self.sender.send_result.assert_called_once_with(result)

    def test_nonfinite_side_becomes_a_saved_validation_error(self):
        self.user.get_sides.return_value = ("nan", "4", "5")
        with self.assertLogs("triangle", level="ERROR"):
            self.controller.run()
        self.assertEqual(self.database.get("nan", "4", "5")["error_message"],
                         "Стороны не образуют треугольник.")

    def test_equilateral_result_is_stored_in_the_same_schema(self):
        self.user.get_sides.return_value = ("5", "5", "5")
        result = self.controller.run()
        self.assertEqual(self.database.get("5", "5", "5")["triangle_type"], "равносторонний")
        self.sender.send_result.assert_called_once_with(result)

    def test_isosceles_result_is_stored_and_sent(self):
        self.user.get_sides.return_value = ("5", "5", "6")
        result = self.controller.run()
        self.assertEqual(self.database.get("5", "5", "6")["triangle_type"], "равнобедренный")
        self.sender.send_result.assert_called_once_with(result)

    def test_different_requests_create_separate_records(self):
        self.user.get_sides.side_effect = [("3", "4", "5"), ("5", "5", "5")]
        self.controller.run()
        self.controller.run()
        self.assertIsNotNone(self.database.get("3", "4", "5"))
        self.assertIsNotNone(self.database.get("5", "5", "5"))
        self.assertEqual(self.calculator.calculate.call_count, 2)

    def test_deleted_result_is_calculated_again(self):
        self.controller.run()
        self.assertTrue(self.database.delete("3", "4", "5"))
        self.controller.run()
        self.assertEqual(self.calculator.calculate.call_count, 2)
        self.assertIsNotNone(self.database.get("3", "4", "5"))

    def test_console_input_with_stubbed_input_reaches_database_and_sender(self):
        controller = Controller(ConsoleInput(), TriangleCalculator(), self.database, self.sender)
        with patch("builtins.input", side_effect=[" 3 ", "4", "5"]) as input_stub:
            result = controller.run()
        self.assertEqual(input_stub.call_count, 3)
        self.assertIsNotNone(self.database.get("3", "4", "5"))
        self.sender.send_result.assert_called_once_with(result)

    def test_sender_failure_keeps_saved_result_for_retry(self):
        self.sender.send_result.side_effect = [RuntimeError("сервер недоступен"), None]
        with self.assertRaisesRegex(RuntimeError, "сервер недоступен"):
            self.controller.run()
        self.assertIsNotNone(self.database.get("3", "4", "5"))
        self.assertEqual(self.controller.run(), "разносторонний")
        self.calculator.calculate.assert_called_once()
        self.assertEqual(self.sender.send_result.call_count, 2)

    def test_database_save_failure_prevents_sending_unsaved_result(self):
        with patch.object(self.database, "add", side_effect=sqlite3.OperationalError("ошибка БД")):
            with self.assertRaises(sqlite3.OperationalError):
                self.controller.run()
        self.sender.send_result.assert_not_called()
        self.assertIsNone(self.database.get("3", "4", "5"))

    def test_database_read_failure_prevents_calculation_and_sending(self):
        with patch.object(self.database, "get", side_effect=sqlite3.OperationalError("ошибка чтения")):
            with self.assertRaises(sqlite3.OperationalError):
                self.controller.run()
        self.calculator.calculate.assert_not_called()
        self.sender.send_result.assert_not_called()

    def test_interrupted_input_does_not_store_or_send_anything(self):
        self.user.get_sides.side_effect = EOFError("ввод завершён")
        with self.assertRaises(EOFError):
            self.controller.run()
        self.assertIsNone(self.database.get("3", "4", "5"))
        self.calculator.calculate.assert_not_called()
        self.sender.send_result.assert_not_called()

    def test_internal_calculation_error_is_logged_saved_and_sent(self):
        with patch("triangle._calculate_coordinates", side_effect=RuntimeError("сбой расчёта")):
            with self.assertLogs("triangle", level="ERROR") as logs:
                result = self.controller.run()
        self.assertIsNotNone(logs.records[0].exc_info)
        self.assertEqual(self.database.get("3", "4", "5")["triangle_type"], "не треугольник")
        self.sender.send_result.assert_called_once_with(result)

    def test_file_database_retains_cache_after_reopening(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "triangles.sqlite3"
            first_database = TriangleDatabase(path)
            try:
                Controller(self.user, TriangleCalculator(), first_database, self.sender).run()
            finally:
                first_database.close()
            second_database = TriangleDatabase(path)
            try:
                calculator = create_autospec(TriangleCalculator, instance=True)
                result = Controller(self.user, calculator, second_database, self.sender).run()
                self.assertEqual(result, "разносторонний")
                calculator.calculate.assert_not_called()
            finally:
                second_database.close()
