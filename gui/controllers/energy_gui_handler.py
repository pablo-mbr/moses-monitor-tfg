from PyQt6.QtWidgets import QMessageBox, QStackedWidget

from colors import RED, GREEN
from log_types import LogType
from core.models.energy_model import EnergyModel
from gui.components.terminal import Terminal
from gui.components.consumption_graph import ConsumptionGraph


class EnergyGuiHandler:
    def __init__(
        self,
        model: EnergyModel,
        parent,
        stack: QStackedWidget,
        btn_toggle,
        graph_inst: ConsumptionGraph,
        graph_accum: ConsumptionGraph,
        label_watts,
        input_inst_threshold,
        input_accum_threshold,
        input_baseline,
    ):
        self._model = model
        self._parent = parent
        self._stack = stack
        self._btn_toggle = btn_toggle
        self._graph_inst = graph_inst
        self._graph_accum = graph_accum
        self._label_watts = label_watts

        input_inst_threshold.textChanged.connect(self._on_inst_threshold_changed)
        input_accum_threshold.textChanged.connect(self._on_accum_threshold_changed)
        input_baseline.textChanged.connect(self._on_baseline_changed)

        self._model.inst_threshold_exceeded.connect(self._on_power_exceeded)
        self._model.accum_threshold_exceeded.connect(self._on_consumption_exceeded)
        self._blocked_alerts = False

    def update(self, value: float):
        self._graph_inst.curve.setData(self._model.data_y)
        self._graph_accum.curve.setData(self._model.data_accum)
        self._label_watts.setText(f"{value:.1f} W")
        self._update_watts_color(value)

    def reset(self):
        self._model.reset()
        self._graph_inst.curve.setData([])
        self._graph_accum.curve.setData([])
        Terminal().log("[SISTEMA] Datos reseteados.", LogType.INFO)

    def toggle_graph(self):
        if self._stack.currentWidget() is self._graph_inst:
            self._stack.setCurrentWidget(self._graph_accum)
            self._btn_toggle.setText("Vista: Potencia")
        else:
            self._stack.setCurrentWidget(self._graph_inst)
            self._btn_toggle.setText("Vista: Consumo")

    def _on_inst_threshold_changed(self, text: str):
        if not text.strip():
            self._model.inst_threshold = None
            self._graph_inst.threshold_line.setVisible(False)
        else:
            try:
                self._model.inst_threshold = float(text)
                self._graph_inst.threshold_line.setPos(self._model.inst_threshold)
                self._graph_inst.threshold_line.setVisible(True)
            except ValueError:
                pass

    def _on_accum_threshold_changed(self, text: str):
        if not text.strip():
            self._model.accum_threshold = None
            self._graph_accum.threshold_line.setVisible(False)
        else:
            try:
                self._model.accum_threshold = float(text)
                self._graph_accum.threshold_line.setPos(self._model.accum_threshold)
                self._graph_accum.threshold_line.setVisible(True)
            except ValueError:
                pass

    def _on_baseline_changed(self, text: str):
        if not text.strip():
            self._model.baseline = None
            self._graph_inst.baseline_line.setVisible(False)
        else:
            try:
                self._model.baseline = float(text)
                self._graph_inst.baseline_line.setPos(self._model.baseline)
                self._graph_inst.baseline_line.setVisible(True)
            except ValueError:
                pass

    def _update_watts_color(self, value: float):
        color = RED if self._model.inst_threshold is not None and value > self._model.inst_threshold else GREEN
        self._label_watts.setStyleSheet(f"font-size: 42px; font-weight: 800; color: {color};")

    def _on_power_exceeded(self, value: float):
        Terminal().log(f"[ENERGÍA] Umbral de potencia superado: {value:.1f} W. Umbral: {self._model.inst_threshold} W", LogType.WARNING)
        if not self._blocked_alerts:
            self._blocked_alerts = True
            msg = QMessageBox(self._parent)
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setWindowTitle("ALERTA POTENCIA")
            msg.setText(f"Potencia excesiva: {value:.1f} W")
            msg.finished.connect(lambda _: setattr(self, '_blocked_alerts', False))
            msg.show()

    def _on_consumption_exceeded(self, value: float):
        Terminal().log(f"[ENERGÍA] Umbral de consumo total alcanzado: {value:.1f} J. Umbral: {self._model.accum_threshold} J", LogType.WARNING)
        if not self._blocked_alerts:
            self._blocked_alerts = True
            msg = QMessageBox(self._parent)
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setWindowTitle("ALERTA CONSUMO TOTAL")
            msg.setText(f"Umbral de consumo total alcanzado: {value:.1f} J.")
            msg.finished.connect(lambda _: setattr(self, '_blocked_alerts', False))
            msg.show()
