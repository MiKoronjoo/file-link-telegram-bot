import sqlite3

from pyrogram import Client, Message
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


def get_admin(telegram_id):
    res = exe_query(f'SELECT * FROM Admin WHERE telegram_id = {telegram_id};')
    return None if not res else res[0]


def set_caption(admin: tuple, caption: str):
    caption = caption.replace("'", '"')
    exe_query(f"UPDATE Media SET caption = '{caption}' WHERE file_id = {admin[1]};")
    exe_query(f'UPDATE Admin SET file_id = null WHERE telegram_id = {admin[0]};')


def get_caption(file_id: str):
    return 'caption'  # TODO: get caption from database


client = Client(session_name='my_bot',
                api_id=API_ID,
                api_hash=API_HASH,
                bot_token=BOT_TOKEN,
                proxy=PROXY
                )


@client.on_message()
def handle_message(bot: Client, msg: Message):
    admin = get_admin(msg.chat.id)
    if admin:
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
        bot.send_message(msg.chat.id, f't.me/{BOT_USERNAME}/?start={file_id}')
    elif msg.text and msg.text.startswith('/start '):
        file_id = msg.text.split()[-1]
        decode = decode_file_id(file_id)
        media_type = BaseClient.MEDIA_TYPE_ID[decode[0]]
        try:
            bot.__getattribute__(f'send_{media_type}')(msg.chat.id, file_id, caption=get_caption(file_id))
        except AttributeError:
            bot.send_message(msg.chat.id, "Can't send file")
    else:
        bot.send_message(msg.chat.id, 'Please use file links')


if __name__ == '__main__':
    client.run()
