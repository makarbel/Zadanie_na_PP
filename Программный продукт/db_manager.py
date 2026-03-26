import psycopg2
from psycopg2 import extras

class DBManager:
    def __init__(self):
        self.conn_params = {
            "dbname": "db_3",
            "user": "postgres",
            "password": "12345",
            "host": "localhost",
            "port": "5433"
        }
        self._create_table_if_not_exists()

    def _get_connection(self):
        return psycopg2.connect(**self.conn_params)

    def _create_table_if_not_exists(self):
        commands = (
            """
            CREATE TABLE IF NOT EXISTS Users (
                id SERIAL PRIMARY KEY,
                login VARCHAR(50) UNIQUE NOT NULL,
                password VARCHAR(50) NOT NULL,
                role VARCHAR(20) NOT NULL CHECK (role IN ('Администратор', 'Пользователь')),
                is_blocked BOOLEAN DEFAULT FALSE
            )
            """,
            "INSERT INTO Users (login, password, role) SELECT 'admin', 'admin', 'Администратор' WHERE NOT EXISTS (SELECT 1 FROM Users WHERE login = 'admin')"
        )
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    for cmd in commands:
                        cur.execute(cmd)
                conn.commit()
        except Exception as e:
            print(f"DB Error: {e}")

    def get_user(self, login):
        try:
            with self._get_connection() as conn:
                with conn.cursor(cursor_factory=extras.RealDictCursor) as cur:
                    cur.execute("SELECT * FROM Users WHERE login = %s", (login,))
                    return cur.fetchone()
        except Exception as e:
            return None

    def get_all_users(self):
        try:
            with self._get_connection() as conn:
                with conn.cursor(cursor_factory=extras.RealDictCursor) as cur:
                    cur.execute("SELECT login, role, is_blocked FROM Users ORDER BY login")
                    return cur.fetchall()
        except Exception as e:
            return []

    def add_user(self, login, password, role):
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("INSERT INTO Users (login, password, role) VALUES (%s, %s, %s)", (login, password, role))
                conn.commit()
                return True
        except Exception as e:
            return False

    def block_user(self, login):
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("UPDATE Users SET is_blocked = TRUE WHERE login = %s", (login,))
                conn.commit()
        except Exception as e:
            pass

    def toggle_block_status(self, login):
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("UPDATE Users SET is_blocked = NOT is_blocked WHERE login = %s", (login,))
                conn.commit()
                return True
        except Exception as e:
            return False