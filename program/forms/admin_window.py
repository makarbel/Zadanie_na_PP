from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                             QTableWidgetItem, QPushButton, QLineEdit,
                             QComboBox, QMessageBox, QHeaderView, QCheckBox, QDialog,
                             QFormLayout, QDialogButtonBox, QLabel)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QColor


class UserEditDialog(QDialog):
    """Отдельное диалоговое окно для добавления и редактирования пользователя."""

    def __init__(self, parent=None, user=None):
        super().__init__(parent)
        self.user = user
        is_edit = user is not None
        self.setWindowTitle("Редактировать пользователя" if is_edit else "Добавить пользователя")
        self.setMinimumWidth(340)
        self._init_ui(is_edit)

    def _init_ui(self, is_edit):
        layout = QFormLayout(self)

        self.edit_login = QLineEdit()
        self.edit_login.setPlaceholderText("Логин")
        if self.user:
            self.edit_login.setText(self.user.login)
        layout.addRow("Логин:", self.edit_login)

        self.edit_pass = QLineEdit()
        self.edit_pass.setPlaceholderText("Пароль" if not is_edit else "Новый пароль (или пусто)")
        # Поле пароля скрытое согласно требованию п. 5.8
        self.edit_pass.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addRow("Пароль:", self.edit_pass)

        self.role_combo = QComboBox()
        self.role_combo.addItems(["Администратор", "Пользователь"])
        if self.user:
            self.role_combo.setCurrentText(self.user.role)
        layout.addRow("Роль:", self.role_combo)

        if is_edit:
            self.check_blocked = QCheckBox("Заблокирован")
            self.check_blocked.setChecked(self.user.is_blocked)
            layout.addRow("Статус:", self.check_blocked)
        else:
            self.check_blocked = None

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def get_data(self):
        return {
            "login": self.edit_login.text().strip(),
            "password": self.edit_pass.text().strip(),
            "role": self.role_combo.currentText(),
            "is_blocked": self.check_blocked.isChecked() if self.check_blocked else False
        }


class AdminWindow(QWidget):
    logout_requested = pyqtSignal()

    def __init__(self, db):
        super().__init__()
        self.db = db
        self.selected_login = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Панель администратора - ООО Молочный комбинат")
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
        self.table.setHorizontalHeaderLabels(["Логин", "Роль", "Статус"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.itemSelectionChanged.connect(self._on_user_selected)
        layout.addWidget(self.table)

        btn_layout = QHBoxLayout()

        btn_add = QPushButton("Добавить")
        btn_add.clicked.connect(self._add_user)

        self.btn_edit = QPushButton("Редактировать")
        self.btn_edit.clicked.connect(self._edit_user)
        self.btn_edit.setEnabled(False)

        self.btn_unblock = QPushButton("Снять блокировку")
        self.btn_unblock.clicked.connect(self._unblock_user)
        self.btn_unblock.setEnabled(False)

        self.btn_delete = QPushButton("Удалить")
        self.btn_delete.clicked.connect(self._delete_user)
        self.btn_delete.setEnabled(False)

        btn_layout.addWidget(btn_add)
        btn_layout.addWidget(self.btn_edit)
        btn_layout.addWidget(self.btn_unblock)
        btn_layout.addWidget(self.btn_delete)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        self.load_data()

    def _on_user_selected(self):
        selected = self.table.selectedItems()
        if not selected:
            self.selected_login = None
            self.btn_edit.setEnabled(False)
            self.btn_unblock.setEnabled(False)
            self.btn_delete.setEnabled(False)
            return
        row = self.table.currentRow()
        self.selected_login = self.table.item(row, 0).text()
        is_blocked = self.table.item(row, 2).text() == "Заблокирован"
        self.btn_edit.setEnabled(True)
        self.btn_unblock.setEnabled(is_blocked)
        self.btn_delete.setEnabled(True)

    def load_data(self):
        users = self.db.get_all_users()
        self.table.setRowCount(len(users))
        for row, user in enumerate(users):
            is_blocked = user.is_blocked
            status_text = "Заблокирован" if is_blocked else "Активен"
            items = [
                QTableWidgetItem(user.login),
                QTableWidgetItem(user.role),
                QTableWidgetItem(status_text)
            ]
            for item in items:
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                if is_blocked:
                    item.setBackground(QColor(255, 200, 200))
            for col, item in enumerate(items):
                self.table.setItem(row, col, item)

    def _add_user(self):
        dialog = UserEditDialog(self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        data = dialog.get_data()
        if not data["login"] or not data["password"]:
            QMessageBox.warning(self, "Ошибка", "Логин и пароль обязательны.")
            return
        if self.db.get_user(data["login"]):
            QMessageBox.critical(self, "Ошибка", f"Пользователь «{data['login']}» уже существует.")
            return
        if self.db.add_user(data["login"], data["password"], data["role"]):
            self.load_data()

    def _edit_user(self):
        if not self.selected_login:
            return
        user = self.db.get_user(self.selected_login)
        if not user:
            return
        dialog = UserEditDialog(self, user)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        data = dialog.get_data()
        if not data["login"]:
            QMessageBox.warning(self, "Ошибка", "Логин не может быть пустым.")
            return
        if data["login"] != self.selected_login and self.db.get_user(data["login"]):
            QMessageBox.critical(self, "Ошибка", f"Пользователь «{data['login']}» уже существует.")
            return
        # Если пароль не введён — оставляем старый
        password = data["password"] if data["password"] else user.password
        if self.db.update_user(self.selected_login, data["login"], password, data["role"]):
            # Обновляем статус блокировки
            if data["is_blocked"]:
                self.db.block_user(data["login"])
            else:
                self.db.unblock_user(data["login"])
            QMessageBox.information(self, "Успех", "Данные пользователя обновлены.")
            self.selected_login = None
            self.load_data()

    def _unblock_user(self):
        if not self.selected_login:
            return
        if self.db.unblock_user(self.selected_login):
            QMessageBox.information(self, "Успех", f"Пользователь «{self.selected_login}» разблокирован.")
            self.load_data()

    def _delete_user(self):
        if not self.selected_login:
            return
        reply = QMessageBox.question(
            self, "Подтверждение",
            f"Вы уверены, что хотите удалить пользователя «{self.selected_login}»?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            if self.db.delete_user(self.selected_login):
                self.selected_login = None
                self.load_data()
