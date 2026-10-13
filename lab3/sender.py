"""Имитация внешнего сервера: реальных сетевых запросов нет."""

from interfaces import ResultSender


class SimulatedSender(ResultSender):
    def send_result(self, message: str) -> None:
        # По заданию нужна только имитация передачи, поэтому достаточно вывода.
        print(f"[Имитация отправки на сервер] {message}")
