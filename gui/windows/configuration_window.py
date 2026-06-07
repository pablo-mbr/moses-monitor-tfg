from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QLineEdit,
                             QPushButton, QGridLayout, QMessageBox)
from PyQt6.QtCore import Qt
from gui.components.hint import Hint

from gui.windows.early_stopping_config_window import EarlyStoppingConfigWindow


# --- VENTANA DE CONFIGURACIÓN INICIAL ---
class ConfigWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Configuración")
        self.setFixedSize(350, 450)
        self.setWindowFlags(self.windowFlags() & ~
                            Qt.WindowType.WindowContextHelpButtonHint)

        self.config_data = {}
        self._thresholds = (80.0, 5000.0)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("<b>Configuración de Umbrales y Alertas</b>"))

        grid_rules = QGridLayout()
        grid_rules.addWidget(QLabel("Umbral de Potencia (W):"), 0, 0)
        self._input_inst = QLineEdit("")
        grid_rules.addWidget(self._input_inst, 0, 1)
        grid_rules.addWidget(Hint("inst_threshold"), 0, 2)

        grid_rules.addWidget(QLabel("Umbral de Consumo Total (J):"), 1, 0)
        self._input_accum = QLineEdit("")
        grid_rules.addWidget(self._input_accum, 1, 1)
        grid_rules.addWidget(Hint("accum_threshold"), 1, 2)

        grid_rules.addWidget(QLabel("Baseline (W)"), 2, 0)
        self._input_baseline = QLineEdit("")
        grid_rules.addWidget(self._input_baseline, 2, 1)
        grid_rules.addWidget(Hint("baseline"), 2, 2)

        self._early_stopping_config_dialog = EarlyStoppingConfigWindow()
        self._btn_early_stopping = QPushButton("Configurar Early Stopping")
        self._btn_early_stopping.clicked.connect(self._open_early_stopping_config_dialog)
        grid_rules.addWidget(self._btn_early_stopping, 3, 0, 1, 3)

        layout.addLayout(grid_rules)

        layout.addWidget(QLabel("<hr>"))

        layout.addWidget(QLabel("<b>Credenciales Tapo P110/P115</b>"))

        grid_credentials = QGridLayout()

        grid_credentials.addWidget(QLabel("Email (TP-Link):"), 0, 0)
        self._input_email = QLineEdit("")
        grid_credentials.addWidget(self._input_email, 1, 0, 1, 2)
        grid_credentials.addWidget(Hint("email"), 1, 2)

        grid_credentials.addWidget(QLabel("Contraseña:"), 2, 0)
        self._input_pass = QLineEdit()
        self._input_pass.setEchoMode(QLineEdit.EchoMode.Password)
        grid_credentials.addWidget(self._input_pass, 3, 0, 1, 2)
        grid_credentials.addWidget(Hint("password"), 3, 2)

        grid_credentials.addWidget(QLabel("IP del Enchufe:"), 4, 0)
        self._input_ip = QLineEdit("")
        grid_credentials.addWidget(self._input_ip, 4, 1)
        grid_credentials.addWidget(Hint("ip"), 4, 2)

        layout.addLayout(grid_credentials)

        self._btn_start = QPushButton("Conectar")
        self._btn_start.setStyleSheet(
            "background-color: #27AE60; color: white; font-weight: bold; padding: 10px; margin-top: 10px;")
        self._btn_start.clicked.connect(self._validate_and_close)
        layout.addWidget(self._btn_start)

    def _parse_optional(self, text: str) -> float | None:
        text = text.strip()
        return float(text) if text else None

    def _validate_and_close(self):
        try:
            inst = self._parse_optional(self._input_inst.text())
            accum = self._parse_optional(self._input_accum.text())
            baseline = self._parse_optional(self._input_baseline.text())

            self.config_data = {
                "inst_threshold": inst,
                "accum_threshold": accum,
                "baseline": baseline,
                "ip": self._input_ip.text(),
                "email": self._input_email.text(),
                "pass": self._input_pass.text()
            }

            if not all([self.config_data["ip"], self.config_data["email"], self.config_data["pass"]]):
                raise ValueError("Las credenciales no pueden estar vacías.")

            self.accept()
        except ValueError as e:
            QMessageBox.critical(self, "Error", f"Dato no válido: {e}")

    def _open_early_stopping_config_dialog(self):
        self._early_stopping_config_dialog.exec()
