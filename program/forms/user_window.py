from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QFont


class UserWindow(QWidget):
    """Рабочий стол пользователя с ролью «Пользователь»."""

    logout_requested = pyqtSignal()

    def __init__(self, login):
        super().__init__()
        self.login = login
        self._init_ui()

    def _init_ui(self):
        self.setWindowTitle("Рабочий стол - ООО Молочный комбинат")
        self.setMinimumSize(400, 250)

        layout = QVBoxLayout(self)

        top_layout = QHBoxLayout()
        top_layout.addStretch()
        btn_logout = QPushButton("Выйти")
        btn_logout.clicked.connect(self.logout_requested.emit)
        top_layout.addWidget(btn_logout)
        layout.addLayout(top_layout)

        layout.addStretch()

        welcome = QLabel(f"Добро пожаловать, {self.login}!")
        welcome.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome.setFont(QFont("Arial", 14))
        layout.addWidget(welcome)

        role_label = QLabel("Роль: Пользователь")
        role_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        role_label.setStyleSheet("color: #777;")
        layout.addWidget(role_label)

        layout.addStretch()
