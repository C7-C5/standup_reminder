import os
from datetime import datetime, date
from clients.telegram_client import TelegramClient
import telebot
from dotenv import load_dotenv
from clients.sqlite_client import SQLiteClient, UserHandler
from logging import getLogger, StreamHandler

logger = getLogger(__name__)
logger.addHandler(StreamHandler())
logger.setLevel('INFO')


load_dotenv()
token = os.getenv('TOKEN')
admin_chat_id = os.getenv('ADMIN_CHAT_ID')
user_handler = UserHandler(SQLiteClient('users.db'))


class MyBot(telebot.TeleBot):
    def __init__(self, telegram_client: TelegramClient, user_handler: UserHandler, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.telegram_client = telegram_client
        self.user_handler = user_handler

    def setup(self):
        user_handler.setup()

    def shutdown(self):
        user_handler.shutdown()

client = TelegramClient(token=token, base_url='https://api.telegram.org')
bot = MyBot(token=token, telegram_client=client, user_handler=user_handler)



@bot.message_handler(commands=['start'])
def start(message):
    """
    start function for registration users in database
    """

    user_id = message.from_user.id
    user_name = message.from_user.username
    chat_id = message.chat.id
    new_registration = False

    user = bot.user_handler.get_user(user_id=str(user_id))
    if not user:
        bot.user_handler.create_user(user_id=str(user_id), username=user_name, chat_id=chat_id)
        new_registration = True

    bot.reply_to(message=message, text=f'You are {"already" if not new_registration else ""} registered as {user_name},'
                                       f' your id is {user_id}')


def handle_communication(message):
    """
    callback function for communicate(), that handles message from current user and replies for it
    """
    bot.user_handler.update_date(user_id=message.from_user.id, updated_date=date.today())
    bot.send_message(chat_id=admin_chat_id, text=f'User {message.from_user.username} says: {message.text}')
    bot.reply_to(message=message, text=str('Thanks and have a nice day!'))

@bot.message_handler(commands=['communicate'])
def communicate(message):
    """
    function that requests status from user
    """
    bot.reply_to(message=message, text=str('What have you done yesterday? What are you planning to do today? '
                                           'Do you have any questions or troubles?'))
    bot.register_next_step_handler(message=message, callback=handle_communication)

def create_error_message(error):
    return f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} ::: {error.__class__} ::: {error}'


while True:
    try:
        bot.setup()
        bot.polling()
    except Exception as e:
        error_message = create_error_message(e)
        bot.telegram_client.post(method='sendMessage', params={'text': error_message,
                                                               'chat_id': admin_chat_id})
        logger.error(error_message)
        bot.shutdown()

