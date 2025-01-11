# info.py

# Config Dictionary for all variables
config = {
    "BOT_TOKEN": "your_bot_token_here",  # Your bot's API token from BotFather
    "ADMIN_ID": "your_telegram_id_here",  # Your Telegram ID for forwarding messages
}

# Function to add new settings dynamically
def add_setting(key, value):
    config[key] = value
