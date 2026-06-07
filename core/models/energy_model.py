import csv
import os
from datetime import datetime
from PyQt6.QtCore import QObject, pyqtSignal


class EnergyModel(QObject):
    inst_threshold_exceeded  = pyqtSignal(float)
    accum_threshold_exceeded = pyqtSignal(float)

    def __init__(self, inst_threshold, accum_threshold, baseline):
        super().__init__()
        self.inst_threshold = inst_threshold
        self.accum_threshold = accum_threshold
        self.baseline = baseline
        self.last_measurement = 0.0
        self.total_consumption = 0.0
        self.data_y = []
        self.data_accum = []
        self._inst_exceeded = False
        self._accum_exceeded = False

        os.makedirs("Training Metrics/Consumption Logs", exist_ok=True)
        timestamp = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
        self.csv_file = os.path.join("Training Metrics", "Consumption Logs", f"consumption_{timestamp}.csv")
        self._prepare_csv()

    def _prepare_csv(self):
        with open(self.csv_file, 'w', newline='') as f:
            csv.writer(f).writerow(["timestamp", "watts", "accum"])

    def register_measurement(self, value):
        self.last_measurement = value
        self.data_y.append(value)
        if len(self.data_y) > 100: self.data_y.pop(0)

        self.total_consumption += value
        self.data_accum.append(self.total_consumption)
        if len(self.data_accum) > 100: self.data_accum.pop(0)

        with open(self.csv_file, 'a', newline='') as f:
            csv.writer(f).writerow([datetime.now().isoformat(), round(value, 2), round(self.total_consumption, 2)])

        self._check_thresholds(value)

    def _check_thresholds(self, value: float):
        if self.inst_threshold is not None:
            if value > self.inst_threshold:
                if not self._inst_exceeded:
                    self._inst_exceeded = True
                    self.inst_threshold_exceeded.emit(value)
            else:
                self._inst_exceeded = False

        if self.accum_threshold is not None:
            if self.total_consumption > self.accum_threshold:
                if not self._accum_exceeded:
                    self._accum_exceeded = True
                    self.accum_threshold_exceeded.emit(self.total_consumption)
            else:
                self._accum_exceeded = False


    def reset(self):
        self.data_y, self.data_accum, self.total_consumption = [], [], 0.0
        self._inst_exceeded = False
        self._accum_exceeded = False