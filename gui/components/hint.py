from PyQt6.QtWidgets import QLabel, QStyle

HINTS = {
    "inst_threshold": "Valor en vatios a partir del cual alertar exceso de consumo en un instante.",
    "accum_threshold": "Valor en vatios a partir del cual alertar un exceso de consumo acumulado.",
    "baseline": "Valor medio de consumo base del dispositivo de medición. Algunos ejemplos son:\n  - 7,65W: Portátil, CPU: Intel i7-10750H (2.60 GHz), GPU: NVIDIA GeForce GTX 1650, SO: Windows 11, \n  - 11W: Sobremesa ,CPU: Intel i5-12600KF (3.70 GHz), GPU: NVIDIA GeForce RTX 4070 (12 GB), ALIMENTACIÓN: Seasonic Core GX-650W Gold, SO: Windows 11",
    "email": "Correo electrónico de la cuenta de Tapo asociada.",
    "password": "Contraseña de la cuenta de Tapo asociada.",
    "ip": "Dirección IP del enchufe. Se puede consultar desde la información de dispositivo en la aplicación de Tapo.",
    "metric_name": "Nombre asignado a la métrica en el entrenamiento. Debe coincidir de forma exacta.",
    "tendency": "Tendencia de la métrica: creciente o decreciente.\nEj: accuracy es creciente, loss decreciente.",
    "es_window": "Venatana de mejora para la métrica. Determina la cantidad de recibos de la métrica que se toleran\nsin cierta mejora antes de alertar Early Stopping.",
    "min_var": "Porcentaje de variabilidad mínimo deseable de la métrica.\nSi la métrica no mejora por encima de ese porcentaje con respecto a su mejor valor se alertará Early Stopping.",
    "train_mode": "Modo de entrenamiento sobre el que analizar esta métrica.\nPueden seleccionarse ambos si se desea."
}

class Hint(QLabel):

    def __init__(self, hint_key, parent=None):
        super().__init__(parent)

        icon = self.style().standardIcon(
            QStyle.StandardPixmap.SP_MessageBoxInformation
        )

        self.setPixmap(icon.pixmap(16, 16))

        info = HINTS.get(hint_key, "No hay información adicional.")
        self.setToolTip(info)