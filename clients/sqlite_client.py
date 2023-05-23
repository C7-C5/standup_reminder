import sqlite3
QUERY_CREATE_DB = """
    CREATE TABLE IF NOT EXISTS users (
    user_id int PRIMARY KEY,
    username text,
    chat_id int,
    last_updated_date date
    );
"""


class SQLiteClient:
    def __init__(self, filepath):
        self.filepath = filepath
        self.connector = None

    def setup_connection(self):
        self.connector = sqlite3.connect(self.filepath, check_same_thread=False)

    def close_connection(self):
        self.connector.close()

    def execute_query(self, query, params: tuple):
        if self.connector is not None:
            self.connector.execute(query, params)
            self.connector.commit()
        else:
            raise ConnectionError('You have to connect with DB!')

    def execute_select_query(self, query):
        if self.connector is not None:
            cursor = self.connector.cursor()
            cursor.execute(query)
            return cursor.fetchall()

        else:
            raise ConnectionError('You have to connect with DB!')


class UserHandler:
    QUERY_CREATE_USER = """
        INSERT INTO users (user_id, username, chat_id) VALUES (?, ?, ?)
    """

    QUERY_GET_USER = """
        SELECT user_id, username, chat_id FROM users WHERE user_id = %s
    """

    QUERY_UPDATE_DATE = """
        UPDATE users SET last_updated_date = ? WHERE user_id = ?
    """

    def __init__(self, client: SQLiteClient):
        self.client = client

    def setup(self):
        self.client.setup_connection()

    def shutdown(self):
        self.client.close_connection()

    def create_user(self, user_id, username, chat_id):
        self.client.execute_query(self.QUERY_CREATE_USER, (user_id, username, chat_id))

    def get_user(self, user_id):
        user = self.client.execute_select_query(self.QUERY_GET_USER % user_id)
        return user if user else None

    def update_date(self, user_id, updated_date):
        self.client.execute_query(self.QUERY_UPDATE_DATE, (updated_date, user_id))






