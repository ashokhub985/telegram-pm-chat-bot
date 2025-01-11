from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import info  # Import the info.py file to get the bot token and admin ID

# Use the variables from info.py
BOT_TOKEN = info.BOT_TOKEN
ADMIN_ID = info.ADMIN_ID

# Function to start the bot
def start(update: Update, context: CallbackContext):
    update.message.reply_text("Hello! I am your assistant. You can send me a message and I will forward it to the admin.")

# Function to handle user messages and forward them to admin
def forward_to_admin(update: Update, context: CallbackContext):
    # Forward the message to admin
    context.bot.send_message(chat_id=ADMIN_ID, text=f"Message from {update.message.from_user.first_name}: {update.message.text}")
    
    # Send acknowledgment to the user
    update.message.reply_text("Your message has been forwarded to the admin.")

# Function to handle admin's reply to the user
def admin_reply(update: Update, context: CallbackContext):
    # Check if the sender is the admin
    if update.message.from_user.id == int(ADMIN_ID):
        # Parse the user's message and forward the reply to the user
        user_message = update.message.reply_to_message.text.split(": ")[1]
        user_id = update.message.reply_to_message.forward_from.id

        # Send the reply to the user
        context.bot.send_message(chat_id=user_id, text=f"Admin's reply: {update.message.text}")
        
        update.message.reply_text(f"Reply sent to user: {user_message}")
    else:
        update.message.reply_text("You are not authorized to send admin replies.")

# Main function to handle updates
def main():
    updater = Updater(token=BOT_TOKEN, use_context=True)
    
    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher
    
    # Command handler for the /start command
    dispatcher.add_handler(CommandHandler("start", start))
    
    # Message handler for forwarding user messages to admin
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, forward_to_admin))
    
    # Message handler for admin's replies
    dispatcher.add_handler(MessageHandler(Filters.text & Filters.reply, admin_reply))

    # Start the bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C
    updater.idle()

if __name__ == '__main__':
    main()
