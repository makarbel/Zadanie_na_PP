import sys
from PyQt6.QtWidgets import QApplication, QMessageBox

from utils.db_manager import DBManager
from forms.auth_window import AuthWindow
from forms.admin_window import AdminWindow
from forms.user_window import UserWindow


class MainController:
    def __init__(self):
        try:
            self.db = DBManager()
        except Exception as e:
            QMessageBox.critical(None, "Ошибка подключения", f"Не удалось подключиться к БД:\n{e}")
            sys.exit(1)

        self.current_window = None
        self.show_login()

    def show_login(self):
        self._close_current()
        self.current_window = AuthWindow(self.db)
        self.current_window.login_successful.connect(self.show_dashboard)
        self.current_window.show()

    def show_dashboard(self, login, role):
        self._close_current()
        if role == "Администратор":
            self.current_window = AdminWindow(self.db)
            self.current_window.logout_requested.connect(self.show_login)
        else:
            self.current_window = UserWindow(login)
            self.current_window.logout_requested.connect(self.show_login)
        self.current_window.show()

    def _close_current(self):
        if self.current_window:
            self.current_window.close()
            self.current_window = None


if __name__ == "__main__":
    app = QApplication(sys.argv)
    controller = MainController()
    sys.exit(app.exec())
