from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel, QMessageBox
from PyQt6.QtCore import pyqtSignal, Qt

from forms.captcha_widget import ChallengeCaptchaWidget


class AuthWindow(QWidget):
    login_successful = pyqtSignal(str, str)

    def __init__(self, db_manager):
        super().__init__()
        self.db = db_manager
        self.failed_attempts = 0
        self.last_login = ""
        self._init_ui()

    def _init_ui(self):
        self.setWindowTitle("Авторизация - ООО Молочный комбинат")
        self.setMinimumSize(450, 550)
        layout = QVBoxLayout(self)

        self.login_input = QLineEdit()
        self.login_input.setPlaceholderText("Логин")
        # Сбрасываем счётчик если пользователь сменил логин
        self.login_input.textChanged.connect(self._on_login_changed)

        self.pass_input = QLineEdit()
        self.pass_input.setPlaceholderText("Пароль")
        self.pass_input.setEchoMode(QLineEdit.EchoMode.Password)

        self.captcha_widget = ChallengeCaptchaWidget()
        btn_login = QPushButton("Войти")
        btn_login.clicked.connect(self._handle_login)

        layout.addWidget(QLabel("Логин:"))
        layout.addWidget(self.login_input)
        layout.addWidget(QLabel("Пароль:"))
        layout.addWidget(self.pass_input)
        layout.addWidget(QLabel("Соберите пазл:"))
        layout.addWidget(self.captcha_widget, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(btn_login)

    def _on_login_changed(self, text):
        if text != self.last_login:
            self.failed_attempts = 0
            self.last_login = text

    def _handle_login(self):
        login = self.login_input.text()
        password = self.pass_input.text()

        if not login or not password:
            QMessageBox.warning(self, "Ошибка", "Заполните все поля!")
            return

        if not self.captcha_widget.is_correct():
            self.failed_attempts += 1
            QMessageBox.warning(self, "Ошибка", "Капча не собрана!")
            self._check_block(login)
            return

        user = self.db.get_user(login)

        if user and user.is_blocked:
            QMessageBox.critical(self, "Доступ закрыт", "Вы заблокированы. Обратитесь к администратору.")
            return

        if user and user.password == password:
            self.failed_attempts = 0
            QMessageBox.information(self, "Успех", "Вы успешно авторизовались.")
            self.login_successful.emit(user.login, user.role)
        else:
            self.failed_attempts += 1
            # Точный текст из задания с запятой после «Пожалуйста»
            QMessageBox.warning(
                self, "Ошибка",
                "Вы ввели неверный логин или пароль. "
                "Пожалуйста, проверьте ещё раз введенные данные."
            )
            self._check_block(login)

    def _check_block(self, login):
        if self.failed_attempts >= 3:
            # Блокируем только если пользователь существует в БД
            user = self.db.get_user(login)
            if user:
                self.db.block_user(login)
                QMessageBox.critical(self, "Блокировка", "Вы заблокированы. Обратитесь к администратору.")
            self.failed_attempts = 0
        self.captcha_widget.reset_captcha()
