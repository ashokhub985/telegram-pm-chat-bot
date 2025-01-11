#!/usr/bin/python
# -*- coding: utf-8 -*-

from telegram.ext import Application
import time
import json
import telegram.ext
import telegram
import sys
import datetime
import os
import logging
import threading

# Version
Version_Code = 'v1.1.1'

# Setup logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Define the paths for configuration and data files
PATH = os.path.dirname(os.path.realpath(__file__)) + '/'

# Load the configuration files
CONFIG = json.loads(open(PATH + 'config.json', 'r').read())
LANG = json.loads(open(PATH + 'lang/' + CONFIG['Lang'] + '.json').read())

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
        f.write(json.dumps(CONFIG, indent=4))

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

from telegram.ext import Application

# Initialize the application with token from CONFIG
application = Application.builder().token(CONFIG['Token']).build()

# Replace the use of 'updater' with 'application'
application.run_polling()
dispatcher = updater.dispatcher
me = updater.bot.get_me()
CONFIG['ID'] = me.id
CONFIG['Username'] = '@' + me.username

print(f'Starting... (ID: {CONFIG["ID"]}, Username: {CONFIG["Username"]})')

# Process incoming messages
def process_msg(bot, update):
    global message_list
    init_user(update.message.from_user)

    if CONFIG['Admin'] == 0:
        bot.send_message(chat_id=update.message.from_user.id,
                         text=LANG['please_setup_first'])
        return

    if update.message.from_user.id == CONFIG['Admin']:
        if update.message.reply_to_message:
            if str(update.message.reply_to_message.message_id) in message_list:
                msg = update.message
                sender_id = message_list[str(update.message.reply_to_message.message_id)]['sender_id']
                try:
                    if msg.audio:
                        bot.send_audio(chat_id=sender_id, audio=msg.audio, caption=msg.caption)
                    elif msg.document:
                        bot.send_document(chat_id=sender_id, document=msg.document, caption=msg.caption)
                    elif msg.voice:
                        bot.send_voice(chat_id=sender_id, voice=msg.voice, caption=msg.caption)
                    elif msg.video:
                        bot.send_video(chat_id=sender_id, video=msg.video, caption=msg.caption)
                    elif msg.sticker:
                        bot.send_sticker(chat_id=sender_id, sticker=update.message.sticker)
                    elif msg.photo:
                        bot.send_photo(chat_id=sender_id, photo=msg.photo[0], caption=msg.caption)
                    elif msg.text_markdown:
                        bot.send_message(chat_id=sender_id, text=msg.text_markdown, parse_mode=telegram.ParseMode.MARKDOWN)
                    else:
                        bot.send_message(chat_id=CONFIG['Admin'], text=LANG['reply_type_not_supported'])
                        return
                except Exception as e:
                    if e.message == 'Forbidden: bot was blocked by the user':
                        bot.send_message(chat_id=CONFIG['Admin'], text=LANG['blocked_alert'])
                    else:
                        bot.send_message(chat_id=CONFIG['Admin'], text=LANG['reply_message_failed'])
                    return

                if preference_list[str(update.message.from_user.id)]['notification']:
                    bot.send_message(chat_id=update.message.chat_id, text=LANG['reply_message_sent'] % (preference_list[str(sender_id)]['name'], str(sender_id)), parse_mode=telegram.ParseMode.MARKDOWN)
            else:
                bot.send_message(chat_id=CONFIG['Admin'], text=LANG['reply_to_message_no_data'])
        else:
            bot.send_message(chat_id=CONFIG['Admin'], text=LANG['reply_to_no_message'])
    else:
        if preference_list[str(update.message.from_user.id)]['blocked']:
            bot.send_message(chat_id=update.message.from_user.id, text=LANG['be_blocked_alert'])
            return
        fwd_msg = bot.forward_message(chat_id=CONFIG['Admin'], from_chat_id=update.message.chat_id, message_id=update.message.message_id)
        if fwd_msg.sticker:
            bot.send_message(chat_id=CONFIG['Admin'], text=LANG['info_data'] % (update.message.from_user.full_name, str(update.message.from_user.id)), parse_mode=telegram.ParseMode.MARKDOWN, reply_to_message_id=fwd_msg.message_id)
        if preference_list[str(update.message.from_user.id)]['notification']:
            bot.send_message(chat_id=update.message.from_user.id, text=LANG['message_received_notification'])
        message_list[str(fwd_msg.message_id)] = {'sender_id': update.message.from_user.id}
        threading.Thread(target=save_data).start()

# Process commands
def process_command(bot, update):
    init_user(update.message.from_user)
    id = update.message.from_user.id
    global CONFIG
    global preference_list
    command = update.message.text[1:].replace(CONFIG['Username'], '').lower().split()

    if command[0] == 'start':
        bot.send_message(chat_id=update.message.chat_id, text=LANG['start'])
        return
    elif command[0] == 'version':
        bot.send_message(chat_id=update.message.chat_id, text=f'Telegram Private Message Chat Bot\n{Version_Code}\nhttps://github.com/Netrvin/telegram-pm-chat-bot')
        return
    elif command[0] == 'setadmin':
        if CONFIG['Admin'] == 0:
            CONFIG['Admin'] = int(update.message.from_user.id)
            save_config()
            bot.send_message(chat_id=update.message.chat_id, text=LANG['set_admin_successful'])
        else:
            bot.send_message(chat_id=update.message.chat_id, text=LANG['set_admin_failed'])
        return
    elif command[0] == 'togglenotification':
        preference_list[str(id)]['notification'] = not preference_list[str(id)]['notification']
        threading.Thread(target=save_preference).start()
        if preference_list[str(id)]['notification']:
            bot.send_message(chat_id=update.message.chat_id, text=LANG['togglenotification_on'])
        else:
            bot.send_message(chat_id=update.message.chat_id, text=LANG['togglenotification_off'])
    elif command[0] == 'info':
        if update.message.from_user.id == CONFIG['Admin'] and update.message.chat_id == CONFIG['Admin']:
            if update.message.reply_to_message:
                if str(update.message.reply_to_message.message_id) in message_list:
                    sender_id = message_list[str(update.message.reply_to_message.message_id)]['sender_id']
                    bot.send_message(chat_id=update.message.chat_id, text=LANG['info_data'] % (preference_list[str(sender_id)]['name'], str(sender_id)), parse_mode=telegram.ParseMode.MARKDOWN, reply_to_message_id=update.message.reply_to_message.message_id)
                else:
                    bot.send_message(chat_id=update.message.chat_id, text=LANG['reply_to_message_no_data'])
            else:
                bot.send_message(chat_id=update.message.chat_id, text=LANG['reply_to_no_message'])
        else:
            bot.send_message(chat_id=update.message.chat_id, text=LANG['not_an_admin'])
    elif command[0] == 'ping':
        bot.send_message(chat_id=update.message.chat_id, text='Pong!')
    elif command[0] == 'ban':
        if update.message.from_user.id == CONFIG['Admin'] and update.message.chat_id == CONFIG['Admin']:
            if update.message.reply_to_message:
                if str(update.message.reply_to_message.message_id) in message_list:
                    sender_id = message_list[str(update.message.reply_to_message.message_id)]['sender_id']
                    preference_list[str(sender_id)]['blocked'] = True
                    bot.send_message(chat_id=update.message.chat_id, text=LANG['ban_user'] % (preference_list[str(sender_id)]['name'], str(sender_id)), parse_mode=telegram.ParseMode.MARKDOWN)
                    bot.send_message(chat_id=sender_id, text=LANG['be_blocked_alert'])
                else:
                    bot.send_message(chat_id=update.message.chat_id, text=LANG['reply_to_message_no_data'])
            else:
                bot.send_message(chat_id=update.message.chat_id, text=LANG['reply_to_no_message'])
        else:
            bot.send_message(chat_id=update.message.chat_id, text=LANG['not_an_admin'])
    elif command[0] == 'unban':
        if update.message.from_user.id == CONFIG['Admin'] and update.message.chat_id == CONFIG['Admin']:
            if update.message.reply_to_message:
                if str(update.message.reply_to_message.message_id) in message_list:
                    sender_id = message_list[str(update.message.reply_to_message.message_id)]['sender_id']
                    preference_list[str(sender_id)]['blocked'] = False
                    bot.send_message(chat_id=update.message.chat_id, text=LANG['unban_user'] % (preference_list[str(sender_id)]['name'], str(sender_id)), parse_mode=telegram.ParseMode.MARKDOWN)
                    bot.send_message(chat_id=sender_id, text=LANG['unblocked_alert'])
                else:
                    bot.send_message(chat_id=update.message.chat_id, text=LANG['reply_to_message_no_data'])
            else:
                bot.send_message(chat_id=update.message.chat_id, text=LANG['reply_to_no_message'])
        else:
            bot.send_message(chat_id=update.message.chat_id, text=LANG['not_an_admin'])
    else:
        bot.send_message(chat_id=update.message.chat_id, text=LANG['command_not_found'])

# Add handlers
dispatcher.add_handler(telegram.ext.MessageHandler(telegram.ext.Filters.text & ~telegram.ext.Filters.command, process_msg))
dispatcher.add_handler(telegram.ext.CommandHandler('start', process_command))
dispatcher.add_handler(telegram.ext.CommandHandler('version', process_command))
dispatcher.add_handler(telegram.ext.CommandHandler('setadmin', process_command))
dispatcher.add_handler(telegram.ext.CommandHandler('togglenotification', process_command))
dispatcher.add_handler(telegram.ext.CommandHandler('info', process_command))
dispatcher.add_handler(telegram.ext.CommandHandler('ping', process_command))
dispatcher.add_handler(telegram.ext.CommandHandler('ban', process_command))
dispatcher.add_handler(telegram.ext.CommandHandler('unban', process_command))

# Start the bot
updater.start_polling()
updater.idle()
