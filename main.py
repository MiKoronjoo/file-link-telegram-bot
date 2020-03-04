import sqlite3
import time

from pyrogram import Client, Message, User
from pyrogram.client.ext.utils import decode_file_id
from pyrogram.client.ext.base_client import BaseClient

from config import *


def exe_query(query):
    con_obj = sqlite3.connect(DB_PATH)
    courser = con_obj.execute(query)
    res = courser.fetchall()
    con_obj.commit()
    con_obj.close()
    return res


def add_user(user_id, user_fn, user_ln):
    if user_ln is None:
        user_ln = ''
    exe_query(f"INSERT INTO User VALUES ({user_id}, '{user_fn}', '{user_ln}', {int(time.time())});")


def check(user: User):
    if not exe_query(f'SELECT * FROM User where telegram_id = {user.id};'):
        add_user(user.id, user.first_name, user.last_name)


def statistics():
    all_users = len(exe_query(f'SELECT * FROM User'))
    rec_users = len(exe_query(f'SELECT * FROM User WHERE {int(time.time())} - timestamp < {24 * 60 * 60}'))
    return f'All users count: {all_users}\nRecent users count: {rec_users}'


def get_admin(telegram_id: int):
    res = exe_query(f'SELECT * FROM Admin WHERE telegram_id = {telegram_id};')
    return None if not res else res[0]


def set_file_id(telegram_id: int, file_id: str):
    if not exe_query(f"SELECT * FROM Media WHERE file_id = '{file_id}';"):
        exe_query(f"INSERT INTO Media VALUES ('{file_id}', '');")
    exe_query(f"UPDATE Admin SET file_id = '{file_id}' WHERE telegram_id = {telegram_id};")


def get_media(file_id: str):
    res = exe_query(f"SELECT * FROM Media WHERE file_id = '{file_id}';")
    return None if not res else res[0]


def set_caption(admin: tuple, caption: str):
    caption = caption.replace("'", '"')
    exe_query(f"UPDATE Media SET caption = '{caption}' WHERE file_id = '{admin[1]}';")
    exe_query(f'UPDATE Admin SET file_id = null WHERE telegram_id = {admin[0]};')


client = Client(session_name='my_bot',
                api_id=API_ID,
                api_hash=API_HASH,
                bot_token=BOT_TOKEN,
                proxy=PROXY
                )


@client.on_message()
def handle_message(bot: Client, msg: Message):
    check(msg.from_user)
    admin = get_admin(msg.chat.id)
    if msg.text and msg.text.startswith('/start '):
        file_id = msg.text.split()[-1]
        media = get_media(file_id)
        if not media:
            bot.send_message(msg.chat.id, 'Invalid link')
            return
        decode = decode_file_id(file_id)
        media_type = BaseClient.MEDIA_TYPE_ID[decode[0]]
        try:
            bot.__getattribute__(f'send_{media_type}')(msg.chat.id, file_id, caption=media[1])
        except AttributeError:
            bot.send_message(msg.chat.id, "Can't send file")
    elif admin:
        if msg.text == '/st':
            bot.send_message(msg.chat.id, statistics())
            return
        if msg.document:
            file_id = msg.document.file_id
        elif msg.video:
            file_id = msg.video.file_id
        elif msg.photo:
            file_id = msg.photo.file_id
        elif msg.audio:
            file_id = msg.audio.file_id
        elif msg.voice:
            file_id = msg.voice.file_id
        elif msg.text:
            if admin[1]:
                set_caption(admin, msg.text)
                bot.send_message(msg.chat.id, 'Caption set successfully')
            else:
                bot.send_message(msg.chat.id, 'First, send a file')
            return
        else:
            bot.send_message(msg.chat.id, 'Send a valid file!')
            return
        set_file_id(admin[0], file_id)
        bot.send_message(msg.chat.id, f't.me/{BOT_USERNAME}/?start={file_id}')
    else:
        bot.send_message(msg.chat.id, 'Please use file links')


if __name__ == '__main__':
    client.run()
