# main.py
from config import bot_token, Admin, Lang, Username, ID
import asyncio
import json
import time
import os
import logging
import threading
import telegram
from telegram.ext import Application, MessageHandler, Filters

# Version
Version_Code = 'v1.1.1'

# Setup logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Define the paths for configuration and data files
PATH = os.path.dirname(os.path.realpath(__file__)) + '/'

# Load the language file
LANG = json.loads(open(PATH + 'lang/' + Lang + '.json').read())

# Locks for data consistency
MESSAGE_LOCK = False
PREFERENCE_LOCK = False

# Load message and preference data
message_list = json.loads(open(PATH + 'data.json', 'r').read())
preference_list = json.loads(open(PATH + 'preference.json', 'r').read())

# Functions to save data and preferences
def save_data():
    global MESSAGE_LOCK
    while MESSAGE_LOCK:
        time.sleep(0.05)
    MESSAGE_LOCK = True
    with open(PATH + 'data.json', 'w') as f:
        f.write(json.dumps(message_list))
    MESSAGE_LOCK = False

def save_preference():
    global PREFERENCE_LOCK
    while PREFERENCE_LOCK:
        time.sleep(0.05)
    PREFERENCE_LOCK = True
    with open(PATH + 'preference.json', 'w') as f:
        f.write(json.dumps(preference_list))
    PREFERENCE_LOCK = False

def save_config():
    with open(PATH + 'config.json', 'w') as f:
        f.write(json.dumps({
            'bot_token': bot_token,
            'Admin': Admin,
            'Lang': Lang,
            'Username': Username,
            'ID': ID
        }, indent=4))

def init_user(user):
    global preference_list
    if str(user.id) not in preference_list:
        preference_list[str(user.id)] = {
            'notification': False,
            'blocked': False,
            'name': user.full_name
        }
        threading.Thread(target=save_preference).start()
        return

    if not 'blocked' in preference_list[str(user.id)]:
        preference_list[str(user.id)]['blocked'] = False

    if preference_list[str(user.id)]['name'] != user.full_name:
        preference_list[str(user.id)]['name'] = user.full_name
        threading.Thread(target=save_preference).start()

async def main():
    application = Application.builder().token(bot_token).build()
    bot = application.bot

    # Correct way to call 'get_me' as it is an async function
    me = await bot.get_me()

    # After awaiting, you can access 'me.id' without error
    ID = me.id
    print(ID)

    # Update the Username in config
    global Username
    Username = '@' + me.username

    print(f'Starting... (ID: {ID}, Username: {Username})')

    # Process incoming messages
    async def process_msg(update, context):
        global message_list
        bot = context.bot
        init_user(update.message.from_user)

        if Admin == 0:
            await bot.send_message(chat_id=update.message.from_user.id,
                                   text=LANG['please_setup_first'])
            return

        if update.message.from_user.id == Admin:
            if update.message.reply_to_message:
                if str(update.message.reply_to_message.message_id) in message_list:
                    msg = update.message
                    sender_id = message_list[str(update.message.reply_to_message.message_id)]['sender_id']
                    try:
                        if msg.audio:
                            await bot.send_audio(chat_id=sender_id, audio=msg.audio, caption=msg.caption)
                        elif msg.document:
                            await bot.send_document(chat_id=sender_id, document=msg.document, caption=msg.caption)
                        elif msg.voice:
                            await bot.send_voice(chat_id=sender_id, voice=msg.voice, caption=msg.caption)
                        elif msg.video:
                            await bot.send_video(chat_id=sender_id, video=msg.video, caption=msg.caption)
                        elif msg.sticker:
                            await bot.send_sticker(chat_id=sender_id, sticker=update.message.sticker)
                        elif msg.photo:
                            await bot.send_photo(chat_id=sender_id, photo=msg.photo[0], caption=msg.caption)
                        elif msg.text_markdown:
                            await bot.send_message(chat_id=sender_id, text=msg.text_markdown, parse_mode=telegram.ParseMode.MARKDOWN)
                        else:
                            await bot.send_message(chat_id=Admin, text=LANG['reply_type_not_supported'])
                            return
                    except Exception as e:
                        if e.message == 'Forbidden: bot was blocked by the user':
                            await bot.send_message(chat_id=Admin, text=LANG['blocked_alert'])
                        else:
                            await bot.send_message(chat_id=Admin, text=LANG['reply_message_failed'])
                        return

                    if preference_list[str(update.message.from_user.id)]['notification']:
                        await bot.send_message(chat_id=update.message.chat_id, text=LANG['reply_message_sent'] % (preference_list[str(sender_id)]['name'], str(sender_id)), parse_mode=telegram.ParseMode.MARKDOWN)
                else:
                    await bot.send_message(chat_id=Admin, text=LANG['reply_to_message_no_data'])
            else:
                await bot.send_message(chat_id=Admin, text=LANG['reply_to_no_message'])
        else:
            if preference_list[str(update.message.from_user.id)]['blocked']:
                await bot.send_message(chat_id=update.message.from_user.id, text=LANG['be_blocked_alert'])
                return
            fwd_msg = await bot.forward_message(chat_id=Admin, from_chat_id=update.message.chat_id, message_id=update.message.message_id)
            if fwd_msg.sticker:
                await bot.send_message(chat_id=Admin, text=LANG['info_data'] % (update.message.from_user.full_name, str(update.message.from_user.id)), parse_mode=telegram.ParseMode.MARKDOWN, reply_to_message_id=fwd_msg.message_id)
            if preference_list[str(update.message.from_user.id)]['notification']:
                await bot.send_message(chat_id=update.message.from_user.id, text=LANG['message_received_notification'])
            message_list[str(fwd_msg.message_id)] = {'sender_id': update.message.from_user.id}
            threading.Thread(target=save_data).start()

    # Process commands
    async def process_command(update, context):
        bot = context.bot
        init_user(update.message.from_user)
        id = update.message.from_user.id
        command = update.message.text[1:].replace(Username, '').lower().split()

        if command[0] == 'start':
            await bot.send_message(chat_id=update.message.chat_id, text=LANG['start'])
            return
        elif command[0] == 'version':
            await bot.send_message(chat_id=update.message.chat_id, text=f'Telegram Private Message Chat Bot\n{Version_Code}\nhttps://github.com/Netrvin/telegram-pm-chat-bot')
            return
        elif command[0] == 'setadmin':
            if Admin == 0:
                Admin = int(update.message.from_user.id)
                save_config()
                await bot.send_message(chat_id=update.message.chat_id, text=LANG['set_admin_successful'])
            else:
                await bot.send_message(chat_id=update.message.chat_id, text=LANG['set_admin_failed'])
            return
        elif command[0] == 'togglenotification':
            preference_list[str(id)]['notification'] = not preference_list[str(id)]['notification']
            threading.Thread(target=save_preference).start()
            if preference_list[str(id)]['notification']:
                await bot.send_message(chat_id=update.message.chat_id, text=LANG['togglenotification_on'])
            else:
                await bot.send_message(chat_id=update.message.chat_id, text=LANG['togglenotification_off'])

    # Command handlers
    application.add_handler(MessageHandler(Filters.text & ~Filters.command, process_msg))
    application.add_handler(MessageHandler(Filters.command, process_command))

    # Start the bot
    application.run_polling()

if __name__ == "__main__":
    asyncio.run(main())  # Runs the async function properly
