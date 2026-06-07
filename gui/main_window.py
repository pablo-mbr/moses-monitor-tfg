from PyQt6.QtWidgets import QFileDialog, QDialog
from PyQt6.QtCore import QTimer, pyqtSignal

from core.models.metrics_model import MetricsModel
from gui.layout import AppLayout
from core.models.energy_model import EnergyModel
from gui.windows.historic_window import HistoricWindow
from gui.windows.info_window import InfoWindow
from gui.controllers.energy_gui_handler import EnergyGuiHandler
from gui.controllers.metrics_gui_handler import MetricsGuiHandler
from styles import STYLE_SHEET
from core.communication.dto.metrics_dto import MetricsDto
from core.early_stopping_handler import EarlyStoppingHandler
from log_types import LogType

class MainWindow(AppLayout):
    new_training_metrics = pyqtSignal(MetricsDto)
    reconnection_request = pyqtSignal(dict)

    def __init__(self, inst_threshold, accum_threshold, baseline, data_queue):
        super().__init__()
        self._energy_model = EnergyModel(inst_threshold, accum_threshold, baseline)
        self._results_model = MetricsModel()
        self._data_queue = data_queue
        self.setup_ui(self._energy_model)
        self.resize(1200, 800)
        self.setStyleSheet(STYLE_SHEET)

        self._tapo_stop_event = None
        self._energy = EnergyGuiHandler(
            self._energy_model, self, self.stack, self.btn_toggle,
            self.graph_inst, self.graph_accum,
            self.label_watts, self.input_inst_threshold, self.input_accum_threshold, self.input_baseline
        )
        self._metrics = MetricsGuiHandler(
            self._results_model, self.stack, self.training_container,
            self.graph_training_metrics, self.btn_toggle,
            self.btn_training_metrics, self.btn_next_metric, self.btn_prev_metric,
        )
        self._alert_blocked = False
        EarlyStoppingHandler().early_stopping_detected.connect(self._on_early_stopping_detected)
        self._connect_events()
        self.terminal.log(f"[SESIÓN] {self._energy_model.csv_file}", LogType.INFO)

        self._timer = QTimer()
        self._timer.timeout.connect(self._update_all)
        self._timer.start(1000)

    def _connect_events(self):
        self.btn_reset.clicked.connect(self._energy.reset)
        self.btn_toggle.clicked.connect(self._energy.toggle_graph)
        self.btn_history.clicked.connect(self.open_history)
        self.btn_export.clicked.connect(self.export_logs)
        self.btn_help.clicked.connect(self.open_help)
        self.new_training_metrics.connect(self._metrics.process_new_training_metrics)
        self.btn_reconnect.clicked.connect(self.emit_config)
        self.btn_early_stopping_config.clicked.connect(self.open_early_stopping_config_dialog)

    def _update_all(self):
        while not self._data_queue.empty():
            dato = self._data_queue.get_nowait()
            if isinstance(dato, str):
                self.terminal.log(dato, LogType.ERROR)
            else:
                self._energy_model.register_measurement(dato)

        valor = self._energy_model.last_measurement
        self._energy.update(valor)

    def open_history(self):
        v = HistoricWindow(self)
        v.show()

    def export_logs(self):
        path, _ = QFileDialog.getSaveFileName(self, "Guardar Logs", "Logs.csv", "CSV (*.csv)")
        if path:
            with open(path, 'w', encoding='utf-8') as f: f.write(self.terminal.toPlainText())

    def open_help(self):
        modal = InfoWindow(self)
        modal.show()

    def emit_config(self):
        from gui.windows.configuration_window import ConfigWindow
        window = ConfigWindow()
        if window.exec() == QDialog.DialogCode.Accepted:
            self.terminal.log("[SISTEMA] Reiniciando configuración.", LogType.INFO)
            self.terminal.log(f"[MOTOR] Intentando conectar a {window.config_data['ip']}.", LogType.INFO)
            self.reconnection_request.emit(window.config_data)

    def open_early_stopping_config_dialog(self):
        self.early_stopping_config_dialog.exec()

    def _on_early_stopping_detected(self, metric: str, step_type: str, step: int):
        if self._alert_blocked:
            return
        self._alert_blocked = True
        from gui.windows.early_stopping_alert_window import EarlyStoppingAlertWindow
        self.terminal.log(f"[EARLY STOPPING] Situación de early stopping detectada. Métrica: {metric}, {step_type}: {step}.", LogType.ALERT)
        self._alert_window = EarlyStoppingAlertWindow(metric)
        self._alert_window.finished.connect(self._on_alert_closed)
        self._alert_window.show()

    def _on_alert_closed(self):
        self._alert_blocked = False
