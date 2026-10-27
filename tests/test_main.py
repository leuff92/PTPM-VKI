from pathlib import Path
import runpy
import unittest
from unittest.mock import patch

import main


class MainTests(unittest.TestCase):
    def test_valid_input(self):
        with patch("builtins.input", return_value="65.7"):
            with patch("builtins.print") as output:
                main.main()
        output.assert_called_once_with("Результат:", 65)

    def test_zero_input(self):
        with patch("builtins.input", return_value="0.0"):
            with patch("builtins.print") as output:
                main.main()
        self.assertEqual(output.call_args.args[0], "Ошибка:")
        self.assertIsInstance(output.call_args.args[1], ValueError)

    def test_invalid_input(self):
        with patch("builtins.input", return_value="abc"):
            with patch("builtins.print") as output:
                main.main()
        self.assertEqual(output.call_args.args[0], "Ошибка:")
        self.assertIsInstance(output.call_args.args[1], ValueError)

    def test_script_start(self):
        with patch("builtins.input", return_value="100.7"):
            with patch("builtins.print") as output:
                runpy.run_path(str(Path(main.__file__)), run_name="__main__")
        output.assert_called_once_with("Результат:", 1000)
