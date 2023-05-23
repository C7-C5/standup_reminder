import os
import datetime
import time

from clients.sqlite_client import SQLiteClient
from clients.telegram_client import TelegramClient
from logging import getLogger, StreamHandler
from dotenv import load_dotenv

load_dotenv()

db_path = os.getenv('DB_PATH')
logger = getLogger(__name__)
logger.addHandler(StreamHandler())
logger.setLevel('INFO')
last_date = datetime.date.today() - datetime.timedelta(days=1)

token = os.getenv('TOKEN')

class Reminder:
    GET_TASKS = """
        SELECT chat_id FROM users WHERE last_updated_date < date('now');
    """

    def __init__(self, telegram_client: TelegramClient, database_client: SQLiteClient):
        self.telegram_client = telegram_client
        self.database_client = database_client
        self.setted_up = False

    def setup(self):
        self.database_client.setup_connection()
        self.setted_up = True

    def shutdown(self):
        self.database_client.close_connection()

    def notify(self, chat_ids):
        for chat_id in chat_ids:
            response = self.telegram_client.post(method='sendMessage', params={'text': 'You have to report status',
                                                                               'chat_id': chat_id})
            logger.info(response)

    def execute(self):
        chat_ids = self.database_client.execute_select_query(self.GET_TASKS)
        if chat_ids:
            self.notify(chat_ids=[chat_id[0] for chat_id in chat_ids])

    def __call__(self, *args, **kwargs):
        if not self.setted_up:
            logger.error('Worker need to be set up!')
            return None
        self.execute()

if __name__ == '__main__':
    database_client = SQLiteClient(db_path)
    telegram_client = TelegramClient(token=token, base_url='https://api.telegram.org')
    reminder = Reminder(database_client=database_client, telegram_client=telegram_client)
    reminder.setup()
    while True:
        if datetime.date.today() > last_date:
            reminder()
            last_date = datetime.date.today()
        else:
            time.sleep(3600)
