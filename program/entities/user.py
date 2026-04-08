class User:
    """Сущность пользователя системы."""

    def __init__(self, login, password, role, is_blocked):
        self.login = login
        self.password = password
        self.role = role
        self.is_blocked = is_blocked
