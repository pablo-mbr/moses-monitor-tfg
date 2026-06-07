from PyQt6.QtWidgets import QTextEdit
import time
from colors import TEXT_SUBTLE
from log_types import LogType


class Terminal(QTextEdit):
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if Terminal._initialized:
            return
        Terminal._initialized = True
        super().__init__()
        self.setObjectName("Terminal")
        self.setReadOnly(True)

    def log(self, message, log_type=LogType.INFO):
        ts = time.strftime('%H:%M:%S')
        color = log_type.value if isinstance(log_type, LogType) else log_type
        html_msg = f'<span style="color: {TEXT_SUBTLE};">[{ts}]</span> <span style="color: {color};">{message}</span>'
        self.append(html_msg)
        self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())