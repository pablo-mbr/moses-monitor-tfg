from typing import Literal

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QScrollArea, QWidget, QGridLayout, QFrame, QMessageBox, QComboBox
)
from PyQt6.QtCore import Qt

from core.early_stopping_handler import EarlyStoppingHandler, Rule
from gui.components.hint import Hint


class EarlyStoppingConfigWindow(QDialog):
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    modes = {
        "Creciente": "inc",
        "Decreciente": "dec",
    }

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        super().__init__()

        self._handler = EarlyStoppingHandler()

        self.setWindowTitle("Configuración Early Stopping")
        self.setFixedSize(460, 540)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)

        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)

        # --- Formulario ---
        main_layout.addWidget(QLabel("<b><u>Añadir regla</u></b>"))
        rule_info_label = QLabel("Añade las reglas para las métricas sobre las que desees identificar situaciones de early stopping. En caso de detectarse, se otorgará la opción de parar el entrenamiento.")
        rule_info_label.setWordWrap(True)
        main_layout.addWidget(rule_info_label)

        creation_grid = QGridLayout()

        creation_grid.addWidget(QLabel("Nombre de la métrica:"), 0, 0)
        self._input_metric = QLineEdit()
        self._input_metric.setPlaceholderText("ej: loss, accuracy...")
        creation_grid.addWidget(self._input_metric, 0, 1, 1, 2)
        creation_grid.addWidget(Hint("metric_name"), 0, 3)

        creation_grid.addWidget(QLabel("Tendencia de la métrica:"), 1, 0)
        self._dropdown_mode = QComboBox()
        self._dropdown_mode.addItems(["Creciente", "Decreciente"])
        creation_grid.addWidget(self._dropdown_mode, 1, 1, 1, 2)
        creation_grid.addWidget(Hint("tendency"), 1, 3)

        creation_grid.addWidget(QLabel("Paciencia:"), 2, 0)
        self._input_patience = QLineEdit()
        self._input_patience.setPlaceholderText("ej: 5")
        creation_grid.addWidget(self._input_patience, 3, 0)
        creation_grid.addWidget(Hint("es_window"), 3, 1)

        creation_grid.addWidget(QLabel("Variación mínima (%):"), 2, 2)
        self._input_pct = QLineEdit()
        self._input_pct.setPlaceholderText("ej: 1.5")
        creation_grid.addWidget(self._input_pct, 3, 2)
        creation_grid.addWidget(Hint("min_var"), 3, 3)

        main_layout.addLayout(creation_grid)

        self._btn_add = QPushButton("+ Añadir regla")
        self._btn_add.clicked.connect(self._add_rule)
        main_layout.addWidget(self._btn_add)

        # --- Separador ---
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        main_layout.addWidget(line)

        # --- Lista de reglas ---
        main_layout.addWidget(QLabel("<b><u>Reglas configuradas:<u></b>"))

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setMinimumHeight(180)

        rules_container = QWidget()
        self._rules_layout = QVBoxLayout(rules_container)
        self._rules_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self._rules_layout.setSpacing(4)

        self._empty_label = QLabel("Sin reglas configuradas.")
        self._empty_label.setStyleSheet("color: #999; font-style: italic;")
        self._rules_layout.addWidget(self._empty_label)

        scroll_area.setWidget(rules_container)
        main_layout.addWidget(scroll_area)

        # --- Guardar ---
        self._btn_save = QPushButton("Confirmar")
        self._btn_save.clicked.connect(self.close)
        main_layout.addWidget(self._btn_save)

    def _add_rule(self):
        result = self._validate_fields()
        if result is None:
            return

        metric, window, percentage, mode = result
        rule = Rule(patience=window, var_percentage=percentage, mode=mode)
        if self._handler.get_rule(metric):
            QMessageBox.warning(self, "Error de validación", f"Ya existe una regla para {metric}.")
            return
        self._handler.add_rule(metric, rule)
        self._add_rule_row(metric, rule)
        self._input_metric.clear()
        self._input_patience.clear()
        self._input_pct.clear()

    def _validate_fields(self):
        metric = self._input_metric.text().strip()
        patience_text = self._input_patience.text().strip()
        percentage_text = self._input_pct.text().strip()

        errors = []
        if not metric:
            errors.append("El nombre de la métrica no puede estar vacío.")

        patience = None
        if not patience_text:
            errors.append("La paciencia no puede estar vacía.")
        else:
            try:
                patience = int(patience_text)
                if patience <= 0:
                    errors.append("La paciencia debe ser un entero positivo.")
            except ValueError:
                errors.append("La paciencia debe ser un número entero.")

        percentage = None
        if not percentage_text:
            errors.append("La mejora mínima no puede estar vacía.")
        else:
            try:
                percentage = float(percentage_text.replace(',', '.'))
                if percentage < 0:
                    errors.append("La variación mínima debe ser un valor positivo.")
            except ValueError:
                errors.append("La variación mínima debe ser un número decimal.")

        mode_text = self._dropdown_mode.currentText()
        mode = self.modes[mode_text]

        if errors:
            QMessageBox.warning(self, "Error de validación", "\n".join(errors))
            return

        return metric, patience, percentage, mode

    def _add_rule_row(self, metric: str, rule: Rule):
        self._empty_label.setVisible(False)

        label = QLabel(f"{metric} | Tendencia: {rule.mode} | Paciencia: {rule.patience} | Variación: {rule.var_percentage}%")
        label.setWordWrap(True)

        btn_edit = QPushButton("Editar")
        btn_edit.setFixedWidth(55)

        btn_delete = QPushButton("Eliminar")
        btn_delete.setFixedWidth(55)

        row_widget = QWidget()
        row_layout = QHBoxLayout(row_widget)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.addWidget(label)
        row_layout.addWidget(btn_edit)
        row_layout.addWidget(btn_delete)

        btn_delete.clicked.connect(lambda: self._remove_rule_row(metric, row_widget))
        btn_edit.clicked.connect(lambda: self._edit_rule(metric, row_widget))
        self._rules_layout.addWidget(row_widget)

    def _remove_rule_row(self, metric: str, widget: QWidget):
        self._handler.delete_rule(metric)
        widget.deleteLater()
        if not self._handler.get_rules():
            self._empty_label.setVisible(True)

    def _edit_rule(self, metric: str, widget: QWidget):
        rule = self._handler.get_rule(metric)
        if rule is not None:
            self._input_metric.setText(metric)
            self._input_patience.setText(f"{rule.patience}")
            self._input_pct.setText(f"{rule.var_percentage}")
            self._dropdown_mode.setCurrentIndex(self._get_mode_index(rule.mode))
            self._remove_rule_row(metric, widget)

    def _get_mode_index(self, mode: Literal["inc", "dec"]):
        if mode == "inc":
            return 0
        else:
            return 1
