"""Два интерфейса, которые можно заменить заглушками в тестах."""

from abc import ABC, abstractmethod


class UserInput(ABC):
    """Любой способ получения трёх сторон: консоль, окно или тестовая заглушка."""

    @abstractmethod
    def get_sides(self) -> tuple[str, str, str]:
        """Вернуть три строки со сторонами треугольника."""


class ResultSender(ABC):
    """Любой способ передачи строки-результата."""

    @abstractmethod
    def send_result(self, message: str) -> None:
        """Передать результат сторонней зависимости."""
