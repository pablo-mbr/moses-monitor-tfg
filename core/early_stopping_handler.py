from dataclasses import dataclass
from typing import Optional, Literal
from PyQt6.QtCore import QObject, pyqtSignal
from log_types import LogType
from gui.components.terminal import Terminal


@dataclass
class Rule:
    patience: int
    var_percentage: float
    mode: Literal["inc","dec"] = "inc"
    count: int = 0
    best_value: Optional[float] = None


class EarlyStoppingHandler(QObject):
    early_stopping_detected = pyqtSignal(str, str, int)
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if EarlyStoppingHandler._initialized:
            return
        EarlyStoppingHandler._initialized = True
        super().__init__()
        self._rules = {}

    def add_rule(self, metric: str, rule: Rule):
        self._rules[metric] = rule

    def delete_rule(self, metric: str):
        self._rules.pop(metric)

    def get_rules(self) -> dict[str, Rule]:
        return self._rules

    def get_rule(self, metric: str) -> Rule | None:
        if metric in self._rules:
            return self._rules[metric]
        else:
            return None

    def update_phase_state(self, metric: str, value: float, phase: Literal["train", "val"], step: int, step_type: str):
        if phase != "val":
            return
        if metric not in self._rules:
            return
        rule = self._rules[metric]

        if rule.best_value is None:
            rule.best_value = value
            rule.count = 0
            return

        if self._value_is_worse_than_best(rule.best_value, value, rule.mode) or self._is_insufficient_improvement(rule.best_value, value, rule.var_percentage):
            rule.count += 1
            if rule.count >= rule.patience:
                self.early_stopping_detected.emit(metric, step_type, step)
        else:
            rule.count = 0
            rule.best_value = value

    def reset_window(self, metric: str):
        self._rules[metric].count = 0

    def _is_insufficient_improvement(self, best_value: float, value: float, var_percentage: float) -> bool:
        variation = (abs(best_value - value) / best_value) * 100
        return variation < var_percentage

    def _value_is_worse_than_best(self, best_value: float, value: float, mode: Literal["inc", "dec"]) -> bool:
        if mode == "inc":
            return value < best_value
        else:
            return value > best_value

    def send_stop_signal(self):
        from core.communication.mqtt_publisher import MqttPublisher
        self._publisher = MqttPublisher()
        self._publisher.ack.connect(self._on_stop_ack)
        self._publisher.send_early_stopping_signal()

    def _on_stop_ack(self, success: bool):
        if success:
            Terminal().log("[EARLY STOPPING] Señal de parada enviada correctamente.", LogType.SUCCESS)
        else:
            Terminal().log("[EARLY STOPPING] Error al enviar la señal de parada.", LogType.ERROR)
