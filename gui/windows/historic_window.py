import os
from datetime import datetime

import pyqtgraph as pg
from colors import WHITE, GREEN, PURPLE, DARK_GREEN, PHASE_COLORS, PHASE_COLOR_FALLBACK
from PyQt6.QtGui import QBrush
from PyQt6.QtWidgets import (
    QFileDialog, QDialog, QHBoxLayout, QLabel, QMessageBox,
    QPushButton, QVBoxLayout, QLineEdit
)
from PyQt6.QtCore import Qt, QTimer

from core.historic_data_loader import (
    ConsumptionData,
    TrainingMetricsData,
    load_consumption_csv,
    load_training_metrics_csv,
)

# se usa para mostrar el tiempo en el eje x con un formato más legible
class TimeAxisItem(pg.AxisItem):
    def tickStrings(self, values, scale, spacing):
        return [datetime.fromtimestamp(value).strftime("%H:%M:%S") for value in values]


class HistoricWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Análisis de Registro Historico")
        self.resize(1000, 650)

        self._consumption_data: ConsumptionData | None = None
        self._metrics_data: TrainingMetricsData | None = None
        self._consumption_csv_path: str | None = None
        self._metrics_csv_path: str | None = None

        self._current_consumption_key = "inst"
        self._metric_names: list[str] = []
        self._current_metric_index = 0

        self._v_line = None

        self._build_ui()
        self._configure_dual_axis()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        self._label_files = QLabel("Consumo: -- | Métricas: --")
        self._label_files.setStyleSheet(f"font-weight: bold; color: {DARK_GREEN};")
        layout.addWidget(self._label_files)

        self._label_audit_info = QLabel("Use el panel inferior para buscar hitos por Época o por Hora.")
        self._label_audit_info.setStyleSheet("font-weight: 500; color: #2C3E50; background-color: #ECF0F1; padding: 5px; border-radius: 4px;")
        layout.addWidget(self._label_audit_info)

        self._plot_item = pg.PlotItem(axisItems={"bottom": TimeAxisItem(orientation="bottom")})
        self._graph = pg.PlotWidget(plotItem=self._plot_item)
        self._graph.setBackground(WHITE)
        self._graph.showGrid(x=True, y=True)
        self._plot_item.hideButtons()
        layout.addWidget(self._graph)

        self._v_line = pg.InfiniteLine(angle=90, movable=False, pen=pg.mkPen('#E74C3C', width=2, style=Qt.PenStyle.DashLine))
        self._v_line.hide()
        self._plot_item.addItem(self._v_line)

        layout_search = QHBoxLayout()
        self._input_epoch = QLineEdit()
        self._input_epoch.setPlaceholderText("Buscar por Época (ej. 20)")
        self._btn_search_epoch = QPushButton("Ir a Época")

        self._input_time = QLineEdit()
        self._input_time.setPlaceholderText("Buscar por Hora (ej. 17:59:30)")
        self._btn_search_time = QPushButton("Ir a Hora")

        layout_search.addWidget(QLabel("<b>Buscar Época:</b>"))
        layout_search.addWidget(self._input_epoch)
        layout_search.addWidget(self._btn_search_epoch)
        layout_search.addWidget(QLabel("  |  <b>Buscar Hora:</b>"))
        layout_search.addWidget(self._input_time)
        layout_search.addWidget(self._btn_search_time)
        layout.addLayout(layout_search)

        layout_btns = QHBoxLayout()
        self._btn_load_consumption = QPushButton("Importar Consumo")
        self._btn_load_metrics = QPushButton("Importar Métricas")
        self._btn_toggle_consumption = QPushButton("Ver Acumulado")
        self._btn_prev_metric = QPushButton("Métrica Anterior")
        self._btn_next_metric = QPushButton("Métrica Siguiente")

        layout_btns.addWidget(self._btn_load_consumption)
        layout_btns.addWidget(self._btn_load_metrics)
        layout_btns.addWidget(self._btn_toggle_consumption)
        layout_btns.addWidget(self._btn_prev_metric)
        layout_btns.addWidget(self._btn_next_metric)
        layout.addLayout(layout_btns)

        self._btn_load_consumption.clicked.connect(self._select_consumption_csv)
        self._btn_load_metrics.clicked.connect(self._select_metrics_csv)
        self._btn_toggle_consumption.clicked.connect(self._toggle_consumption_mode)
        self._btn_prev_metric.clicked.connect(self._previous_metric)
        self._btn_next_metric.clicked.connect(self._next_metric)

        self._btn_search_epoch.clicked.connect(self._search_by_epoch)
        self._btn_search_time.clicked.connect(self._search_by_time)
        self._input_epoch.returnPressed.connect(self._search_by_epoch)
        self._input_time.returnPressed.connect(self._search_by_time)

    def _configure_dual_axis(self):
        self._metrics_view = pg.ViewBox()
        self._metrics_view.setZValue(100)
        self._plot_item.showAxis("right")
        self._plot_item.scene().addItem(self._metrics_view)
        self._plot_item.getAxis("right").linkToView(self._metrics_view)
        consumption_view = self._plot_item.getViewBox()
        self._metrics_view.setXLink(consumption_view)
        self._metrics_legend = pg.LegendItem(offset=(-10, 10))
        self._metrics_legend.setParentItem(consumption_view)
        self._metrics_legend.anchor(itemPos=(1, 1), parentPos=(1, 1))
        consumption_view.setMouseEnabled(x=False, y=False)
        self._metrics_view.setMouseEnabled(x=False, y=False)
        consumption_view.sigResized.connect(self._sync_views)
        self._sync_views()

    # solo permitimos zoom del eje Y si hay únicamente UN fichero importado por cuestión de proporcionalidad de ejes, que si no se
    # desajusta demasiado la escala entre ambos y se ve fatal
    def _update_zoom_state(self):
        has_consumption = self._consumption_data is not None
        has_metrics = self._metrics_data is not None
        enable_zoom = has_consumption ^ has_metrics

        consumption_view = self._plot_item.getViewBox()
        consumption_view.setMouseEnabled(x=True, y=enable_zoom)
        self._metrics_view.setMouseEnabled(x=True, y=enable_zoom)

    def _sync_views(self):
        consumption_view = self._plot_item.getViewBox()
        self._metrics_view.setGeometry(consumption_view.sceneBoundingRect())
        self._metrics_view.linkedViewChanged(consumption_view, self._metrics_view.XAxis)

    def _select_consumption_csv(self):
        self._select_csv("Importar CSV de consumo", False)

    def _select_metrics_csv(self):
        self._select_csv("Importar CSV de métricas", True)

    def _select_csv(self, caption, metrics):
        path, _ = QFileDialog.getOpenFileName(self, caption, "", "CSV (*.csv)")
        if path:
            if metrics:
                self._load_metrics(path)
            else:
                self._load_consumption(path)

    def _unload_metrics(self):
        self._metrics_csv_path = None
        self._metrics_data = None
        self._btn_load_metrics.setText("Importar Métricas")
        self._btn_load_metrics.clicked.disconnect(self._unload_metrics)
        self._btn_load_metrics.clicked.connect(self._select_metrics_csv)
        self._refresh()

    def _unload_consumption(self):
        self._consumption_csv_path = None
        self._consumption_data = None
        self._btn_load_consumption.setText("Importar Consumo")
        self._btn_load_consumption.clicked.disconnect(self._unload_consumption)
        self._btn_load_consumption.clicked.connect(self._select_consumption_csv)
        self._refresh()

    def _load_consumption(self, path: str):
        self._consumption_data = load_consumption_csv(path)
        self._consumption_csv_path = path
        self._btn_load_consumption.setText("Vaciar Consumo")
        self._btn_load_consumption.clicked.disconnect(self._select_consumption_csv)
        self._btn_load_consumption.clicked.connect(self._unload_consumption)
        self._refresh()

    def _load_metrics(self, path: str):
        self._metrics_data = load_training_metrics_csv(path)
        self._metrics_csv_path = path
        self._metric_names = list(self._metrics_data.series.keys())
        self._current_metric_index = 0
        self._btn_load_metrics.setText("Vaciar Métricas")
        self._btn_load_metrics.clicked.disconnect(self._select_metrics_csv)
        self._btn_load_metrics.clicked.connect(self._unload_metrics)
        self._refresh()

    def _update_labels(self):
        consumption_name = os.path.basename(self._consumption_csv_path) if self._consumption_csv_path else "--"
        metrics_name = os.path.basename(self._metrics_csv_path) if self._metrics_csv_path else "--"
        self._label_files.setText(f"Consumo: {consumption_name} | Metricas: {metrics_name}")

    def _toggle_consumption_mode(self):
        self._current_consumption_key = "accum" if self._current_consumption_key == "inst" else "inst"
        self._btn_toggle_consumption.setText("Ver Instantaneo" if self._current_consumption_key == "accum" else "Ver Acumulado")
        self._refresh()

    def _next_metric(self):
        if not self._metric_names:
            return
        self._current_metric_index = (self._current_metric_index + 1) % len(self._metric_names)
        self._refresh()

    def _previous_metric(self):
        if not self._metric_names:
            return
        self._current_metric_index = (self._current_metric_index - 1) % len(self._metric_names)
        self._refresh()

    def _refresh(self):
        self._update_labels()
        self._update_zoom_state()
        self._plot_item.clear()
        self._metrics_view.clear()
        self._metrics_legend.clear()

        self._v_line = pg.InfiniteLine(angle=90, movable=False, pen=pg.mkPen(color="#E74C3C", width=2, style=Qt.PenStyle.DashLine))
        self._plot_item.addItem(self._v_line)
        self._v_line.hide()

        use_dual_axis = self._consumption_data is not None and self._metrics_data is not None
        if use_dual_axis:
            self._plot_item.showAxis("right")
            self._plot_item.getAxis("right").linkToView(self._metrics_view)
            self._metrics_view.setXLink(self._plot_item.getViewBox())
        else:
            self._plot_item.hideAxis("right")

        all_x = []
        metrics_x = []

        self._refresh_consumption(all_x)
        self._refresh_metrics(all_x, metrics_x, use_dual_axis)

        self._reset_zoom_to_initial(use_dual_axis)

        self._sync_views()

    def _reset_zoom_to_initial(self, use_dual_axis: bool):
        consumption_view = self._plot_item.getViewBox()
        consumption_view.autoRange(padding=0.02)
        if use_dual_axis:
            self._metrics_view.autoRange(padding=0.02)

    def _refresh_consumption(self, all_x: list):
        if self._consumption_data:
            series = self._consumption_data.series[self._current_consumption_key]
            x = [ts.timestamp() for ts in series.timestamps]
            y = series.values
            all_x.extend(x)
            color = GREEN if self._current_consumption_key == "inst" else PURPLE
            self._plot_item.setLabel("left", series.label)
            brush = pg.mkBrush(pg.mkColor(color))
            brush_color = brush.color()
            brush_color.setAlpha(100)
            brush.setColor(brush_color)
            consumption_curve = self._plot_item.plot(
                x,
                y,
                pen=pg.mkPen(color=color, width=1),
                name=series.label,
                fillLevel=0,
                brush=brush,
            )
            consumption_curve.setZValue(-10)
        else:
            self._plot_item.setLabel("left", "Consumo (W)")

    def _refresh_metrics(self, all_x: list, metrics_x: list, use_dual_axis: bool):
        if self._metrics_data and self._metric_names:
            metric_name = self._metric_names[self._current_metric_index]
            phase_series = self._metrics_data.series[metric_name]
            if use_dual_axis:
                self._plot_item.setLabel("right", metric_name)
            else:
                self._plot_item.setLabel("left", metric_name)

            for phase, phase_data in phase_series.items():
                x = [ts.timestamp() for ts in phase_data.timestamps]
                y = phase_data.values
                all_x.extend(x)
                metrics_x.extend(x)
                color = PHASE_COLORS.get(phase, PHASE_COLOR_FALLBACK)
                pen = pg.mkPen(color=color, width=3)
                curve = pg.PlotDataItem(
                    x,
                    y,
                    pen=pen,
                    name=phase,
                    symbol="o",
                    symbolSize=5,
                    symbolBrush=color,
                    symbolPen=pg.mkPen(color=color, width=1),
                )
                curve.setZValue(10)
                if use_dual_axis:
                    self._metrics_view.addItem(curve)
                else:
                    self._plot_item.addItem(curve)
                self._metrics_legend.addItem(curve, phase)
        else:
            self._plot_item.setLabel("right", "Métrica")

    def _search_by_epoch(self):
        if not self._metrics_data or not self._metric_names:
            QMessageBox.warning(self, "Búsqueda", "Primero debe importar un archivo de métricas.")
            return

        text = self._input_epoch.text().strip()
        if not text.isdigit():
            QMessageBox.warning(self, "Búsqueda", "Introduzca un número de época válido.")
            return

        target_epoch = int(text)
        metric_name = self._metric_names[self._current_metric_index]
        phase_series = self._metrics_data.series[metric_name]

        val_train = "N/A"
        val_sub = "N/A"
        target_ts = None

        if "train" in phase_series and target_epoch in phase_series["train"].steps:
            idx_t = phase_series["train"].steps.index(target_epoch)
            val_train = f"{phase_series['train'].values[idx_t]:.4f}"
            target_ts = phase_series["train"].timestamps[idx_t]

        if "val" in phase_series and target_epoch in phase_series["val"].steps:
            idx_v = phase_series["val"].steps.index(target_epoch)
            val_sub = f"{phase_series['val'].values[idx_v]:.4f}"
            if not target_ts:
                target_ts = phase_series["val"].timestamps[idx_v]

        if not target_ts:
            QMessageBox.warning(self, "Búsqueda", f"La época {target_epoch} no tiene registros para la métrica '{metric_name}'.")
            return

        watts_info = "N/A (Cargue CSV consumo)"
        if self._consumption_data:
            c_series = self._consumption_data.series[self._current_consumption_key]
            idx_c = min(range(len(c_series.timestamps)), key=lambda i: abs((c_series.timestamps[i] - target_ts).total_seconds()))
            watts_info = f"{c_series.values[idx_c]:.1f} W"

        self._v_line.setValue(target_ts.timestamp())
        self._v_line.show()
        self._label_audit_info.setText(
            f" <b>Resultado Época {target_epoch}:</b> Hora: {target_ts.strftime('%H:%M:%S')} | "
            f" <b>Train {metric_name}:</b> <span style='color: #2980B9;'>{val_train}</span> | "
            f" <b>Val {metric_name}:</b> <span style='color: #27AE60;'>{val_sub}</span> | "
            f" <b>Consumo en ese instante:</b> <span style='color: #E67E22; font-weight: bold;'>{watts_info}</span>"
        )

    def _search_by_time(self):
        if not self._metrics_data or not self._metric_names:
            QMessageBox.warning(self, "Búsqueda", "Primero debe importar un archivo de métricas.")
            return

        time_str = self._input_time.text().strip()
        metric_name = self._metric_names[self._current_metric_index]
        phase_series = self._metrics_data.series[metric_name]

        ref_phase = "train" if "train" in phase_series else "val"
        if ref_phase not in phase_series or len(phase_series[ref_phase].timestamps) == 0:
            QMessageBox.warning(self, "Búsqueda", "No se han detectado marcas de tiempo válidas.")
            return

        series_ref = phase_series[ref_phase]
        fecha_base = series_ref.timestamps[0].date()

        try:
            target_ts = datetime.strptime(f"{fecha_base} {time_str}", "%Y-%m-%d %H:%M:%S")
        except ValueError:
            QMessageBox.warning(self, "Búsqueda", "Formato de hora incorrecto. Use HH:MM:SS (ej. 17:59:30).")
            return

        idx_ref = min(range(len(series_ref.timestamps)), key=lambda i: abs((series_ref.timestamps[i] - target_ts).total_seconds()))
        nearest_epoch = series_ref.steps[idx_ref]
        ts_real_registro = series_ref.timestamps[idx_ref]

        val_train = "N/A"
        val_sub = "N/A"

        if "train" in phase_series and nearest_epoch in phase_series["train"].steps:
            idx_t = phase_series["train"].steps.index(nearest_epoch)
            val_train = f"{phase_series['train'].values[idx_t]:.4f}"

        if "val" in phase_series and nearest_epoch in phase_series["val"].steps:
            idx_v = phase_series["val"].steps.index(nearest_epoch)
            val_sub = f"{phase_series['val'].values[idx_v]:.4f}"

        watts_info = "N/A"
        if self._consumption_data:
            c_series = self._consumption_data.series[self._current_consumption_key]
            idx_c = min(range(len(c_series.timestamps)), key=lambda i: abs((c_series.timestamps[i] - ts_real_registro).total_seconds()))
            watts_info = f"{c_series.values[idx_c]:.1f} W"

        self._v_line.setValue(ts_real_registro.timestamp())
        self._v_line.show()
        self._label_audit_info.setText(
            f" <b>Resultado Hora {time_str}:</b> Registro más cercano: {ts_real_registro.strftime('%H:%M:%S')} | "
            f" <b>Época localizada:</b> {nearest_epoch} | "
            f" <b>Train {metric_name}:</b> <span style='color: #2980B9;'>{val_train}</span> | "
            f" <b>Val {metric_name}:</b> <span style='color: #27AE60;'>{val_sub}</span> | "
            f" <b>Consumo en ese instante:</b> <span style='color: #E67E22; font-weight: bold;'>{watts_info}</span>"
        )
