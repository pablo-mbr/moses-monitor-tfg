from PyQt6.QtWidgets import QDialog, QVBoxLayout, QTextBrowser, QPushButton
from .info import INFO_CONTENTS

class InfoWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Información adicional")
        self.resize(500, 400)
        
        layout = QVBoxLayout(self)
        
        # Visor de texto (soporta HTML básico)
        self._visor = QTextBrowser()
        self._visor.setHtml(INFO_CONTENTS)
        layout.addWidget(self._visor)

        self._btn_close = QPushButton("Entendido")
        self._btn_close.clicked.connect(self.close)
        layout.addWidget(self._btn_close)