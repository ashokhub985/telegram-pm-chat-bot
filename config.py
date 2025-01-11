from dotenv import load_dotenv
import os

# .env file ko load karein
load_dotenv()

# Variables ko access karein
admin_id = os.getenv("ADMIN_ID")
bot_token = os.getenv("BOT_TOKEN")
lang = os.getenv("LANG")
notification_enabled = os.getenv("NOTIFICATION_ENABLED") == "true"
notification_message = os.getenv("NOTIFICATION_MESSAGE")
command_setadmin = os.getenv("COMMAND_SETADMIN")
command_togglenotification = os.getenv("COMMAND_TOGGLENOTIFICATION")
allowed_ips = os.getenv("ALLOWED_IPS").split(",")
max_message_length = int(os.getenv("MAX_MESSAGE_LENGTH"))
rate_limit_enabled = os.getenv("RATE_LIMIT_ENABLED") == "true"
requests_per_minute = int(os.getenv("REQUESTS_PER_MINUTE"))
logging_enabled = os.getenv("LOGGING_ENABLED") == "true"
log_file = os.getenv("LOG_FILE")
log_level = os.getenv("LOG_LEVEL")

# Output to check values
print(f"Admin ID: {admin_id}")
print(f"Bot Token: {bot_token}")
print(f"Notification Enabled: {notification_enabled}")
print(f"Allowed IPs: {allowed_ips}")
