from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QPushButton, QLabel, QFrame

from core.early_stopping_handler import EarlyStoppingHandler
from gui.windows.early_stopping_config_window import EarlyStoppingConfigWindow


class EarlyStoppingAlertWindow(QDialog):
    _handler = EarlyStoppingHandler()

    def __init__(self, metric: str):
        super().__init__()
        self.setWindowTitle("Alerta Early Stopping")
        self.setFixedSize(300, 250)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)
        self._early_stopping_config_dialog = EarlyStoppingConfigWindow()

        self._metric = metric

        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("<b>⚠ Alerta Early Stopping</b>")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        desc = QLabel(f"Se ha detectado monotonía en la métrica {metric} (validación)\n\n¿Qué desea hacer?")
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc.setWordWrap(True)
        layout.addWidget(desc)

        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(line)

        layout.addStretch()

        self._btn_reset_window = QPushButton("Reiniciar ventana de la métrica")
        self._btn_reset_window.clicked.connect(self._reset_metric_window)
        self._btn_edit_rule = QPushButton("Gestionar regla")
        self._btn_edit_rule.clicked.connect(self._open_early_stopping_config_dialog)
        self._btn_early_stop = QPushButton("Aplicar Early Stopping")
        self._btn_early_stop.clicked.connect(self._apply_early_stopping)

        for btn in (self._btn_reset_window, self._btn_edit_rule, self._btn_early_stop):
            layout.addWidget(btn)

        layout.addStretch()

    def _open_early_stopping_config_dialog(self):
        self._early_stopping_config_dialog.exec()

    def _apply_early_stopping(self):
        self.close()
        self._handler.send_stop_signal()

    def _reset_metric_window(self):
        self._handler.reset_window(self._metric)
        self.close()

    def closeEvent(self, event):
        super().closeEvent(event)
