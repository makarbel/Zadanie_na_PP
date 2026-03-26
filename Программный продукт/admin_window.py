from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
                             QTableWidgetItem, QPushButton, QLineEdit, 
                             QComboBox, QMessageBox, QHeaderView)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QColor

class AdminWindow(QWidget):
    logout_requested = pyqtSignal()

    def __init__(self, db):
        super().__init__()
        self.db = db
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Панель администратора - ООО 'Заказчик'")
        self.setMinimumSize(800, 600)
        layout = QVBoxLayout(self)

        top_layout = QHBoxLayout()
        btn_logout = QPushButton("Выйти")
        btn_logout.clicked.connect(self.logout_requested.emit)
        top_layout.addStretch()
        top_layout.addWidget(btn_logout)
        layout.addLayout(top_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Логин", "Роль", "Статус (Дабл-клик для смены)"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.cellDoubleClicked.connect(self._on_cell_double_clicked)
        layout.addWidget(self.table)

        form = QHBoxLayout()
        self.edit_login = QLineEdit(); self.edit_login.setPlaceholderText("Логин")
        self.edit_pass = QLineEdit(); self.edit_pass.setPlaceholderText("Пароль")
        self.role_combo = QComboBox(); self.role_combo.addItems(["Администратор", "Пользователь"])
        btn_add = QPushButton("Добавить")
        btn_add.clicked.connect(self.add_user)
        form.addWidget(self.edit_login)
        form.addWidget(self.edit_pass)
        form.addWidget(self.role_combo)
        form.addWidget(btn_add)
        layout.addLayout(form)

        self.load_data()

    def _on_cell_double_clicked(self, row, column):
        if column == 2:
            login = self.table.item(row, 0).text()
            if self.db.toggle_block_status(login):
                self.load_data()

    def load_data(self):
        users = self.db.get_all_users()
        self.table.setRowCount(len(users))
        for row, user in enumerate(users):
            is_blocked = user['is_blocked']
            status_text = "Заблокирован" if is_blocked else "Активен"
            items = [QTableWidgetItem(user['login']), QTableWidgetItem(user['role']), QTableWidgetItem(status_text)]
            for item in items:
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable) 
                if is_blocked:
                    item.setBackground(QColor(255, 200, 200))
            for col, item in enumerate(items):
                self.table.setItem(row, col, item)

    def add_user(self):
        login, password = self.edit_login.text(), self.edit_pass.text()
        if not login or not password: return
        if self.db.get_user(login):
            QMessageBox.critical(self, "Ошибка", "Логин занят")
            return
        if self.db.add_user(login, password, self.role_combo.currentText()):
            self.edit_login.clear(); self.edit_pass.clear()
            self.load_data()