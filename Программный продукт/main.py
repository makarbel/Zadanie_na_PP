import sys
from PyQt6.QtWidgets import QApplication, QMessageBox
from db_manager import DBManager
from auth_window import AuthWindow
from admin_window import AdminWindow

class MainController:
    def __init__(self):
        self.db = DBManager()
        self.auth_win = None
        self.admin_win = None
        self.show_login()

    def show_login(self):
        self.auth_win = AuthWindow(self.db)
        self.auth_win.login_successful.connect(self.show_dashboard)
        self.auth_win.show()

    def show_dashboard(self, login, role):
        if self.auth_win:
            self.auth_win.close()
        
        if role == "Администратор":
            self.admin_win = AdminWindow(self.db)
            self.admin_win.logout_requested.connect(self.logout)
            self.admin_win.show()
        else:
            QMessageBox.information(None, "Доступ", f"Добро пожаловать, {login}!")

    def logout(self):
        if self.admin_win:
            self.admin_win.close()
            self.admin_win = None
        self.show_login()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    controller = MainController()
    sys.exit(app.exec())