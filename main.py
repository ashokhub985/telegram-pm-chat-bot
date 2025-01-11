import logging
import time
import threading
from telegram.ext import Application, MessageHandler, Filters
import telegram
import asyncio
import info  # Importing info.py to load configuration dynamically

# Setup logging
if info.LOGGING_ENABLED:
    logging.basicConfig(filename=info.LOG_FILE, level=info.LOG_LEVEL,
                        format='%(asctime)s - %(levelname)s - %(message)s')
else:
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize language data
LANG = json.loads(open(PATH + 'lang/' + info.LANG + '.json').read())

# Assign values from info.py to variables
bot_token = info.BOT_TOKEN
admin_id = info.ADMIN_ID
notification_enabled = info.NOTIFICATION_ENABLED
max_message_length = info.MAX_MESSAGE_LENGTH
rate_limit_enabled = info.RATE_LIMIT_ENABLED
requests_per_minute = info.REQUESTS_PER_MINUTE

# Data storage and locks
message_list = json.loads(open(PATH + 'data.json', 'r').read())
preference_list = json.loads(open(PATH + 'preference.json', 'r').read())

# Function to save data
def save_data():
    global MESSAGE_LOCK
    while MESSAGE_LOCK:
        time.sleep(0.05)
    MESSAGE_LOCK = True
    with open(PATH + 'data.json', 'w') as f:
        f.write(json.dumps(message_list))
    MESSAGE_LOCK = False

# Main bot function
async def main():
    application = Application.builder().token(bot_token).build()
    bot = application.bot

    # Correct way to call 'get_me' as it is an async function
    me = await bot.get_me()

    print(f'Starting bot (ID: {me.id}, Username: @{me.username})')

    # Process incoming messages
    async def process_msg(update, context):
        # Your message processing logic here
        pass

    # Command handlers
    application.add_handler(MessageHandler(Filters.text & ~Filters.command, process_msg))

    # Start the bot
    application.run_polling()

if __name__ == "__main__":
    asyncio.run(main())  # Runs the async function properly
