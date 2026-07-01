import pyqtgraph as pg
from PyQt6.QtCore import Qt
from typing import Literal
from colors import WHITE, ORANGE, RED

GraphMode = Literal["power", "energy"]

Y_LABELS = {
    "power": ("Potencia","W"),
    "energy": ("Consumo Energético","Ws"),
}

class ConsumptionGraph(pg.PlotWidget):
    def __init__(self,  line_color, color_fill, initial_threshold, initial_baseline=None, threshold_color=RED, mode: GraphMode = "power"):
        super().__init__()
        self.setBackground(WHITE)
        label, units = Y_LABELS[mode]
        self.setLabel("left", label, units=units)
        self.setLabel("bottom", "Tiempo", units= "s")
        self.showGrid(x=True, y=True, alpha=0.1)
        self.curve = self.plot(pen=pg.mkPen(color=line_color, width=3),
                               fillLevel=0, brush=color_fill)
        self.threshold_line = pg.InfiniteLine(pos=initial_threshold or 0, angle=0,
                                              pen=pg.mkPen(color=threshold_color, width=2, style=Qt.PenStyle.DashLine))
        self.addItem(self.threshold_line)
        self.threshold_line.setVisible(initial_threshold is not None)
        self.baseline_line = pg.InfiniteLine(pos=initial_baseline or 0, angle=0,
                                             pen=pg.mkPen(color=ORANGE, width=2, style=Qt.PenStyle.DashLine))
        self.addItem(self.baseline_line)
        self.baseline_line.setVisible(initial_baseline is not None)