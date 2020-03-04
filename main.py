from pyrogram import Client, Message
from pyrogram.client.ext.utils import decode_file_id
from pyrogram.client.ext.base_client import BaseClient

from config import *

client = Client(session_name='my_bot',
                api_id=API_ID,
                api_hash=API_HASH,
                bot_token=BOT_TOKEN,
                proxy=PROXY
                )


@client.on_message()
def handle_message(bot: Client, msg: Message):
    if msg.chat.id == ADMIN_ID and any([msg.document, msg.video, msg.photo, msg.audio, msg.voice]):
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
        else:
            bot.send_message(msg.chat.id, 'Never happen!')
            return
        bot.send_message(msg.chat.id, f't.me/{BOT_USERNAME}/?start={file_id}')
    elif msg.text and msg.text.startswith('/start '):
        file_id = msg.text.split()[-1]
        decode = decode_file_id(file_id)
        media_type = BaseClient.MEDIA_TYPE_ID[decode[0]]
        try:
            bot.__getattribute__(f'send_{media_type}')(msg.chat.id, file_id)
        except AttributeError:
            bot.send_message(msg.chat.id, "Can't send file")
    else:
        bot.send_message(msg.chat.id, 'Please use file links')


if __name__ == '__main__':
    client.run()
