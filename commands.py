from telegram import Update
from telegram.ext import CallbackContext

def help_command(update: Update, context: CallbackContext):
    # Provide a list of all available commands
    commands_list = [
        '/help - List of all commands',
        '/users - Number of users that use the bot',
        '/addchannel - Add Channels ',
        '/removechannel - remove channel ',
        '/start - start the process',
        '/stop - stop the process',
        '/reset - Reset the channel.txt file by deleting all content'
        
    ]
    help_message = '\n'.join(commands_list)
    update.message.reply_text(help_message)

def users_command(update: Update, context: CallbackContext):
    # Get the number of users that use the bot
    user_count = len(context.bot_data.get('users', []))
    update.message.reply_text(f"Number of users: {user_count}")

def reset_command(update: Update, context: CallbackContext):
    # Reset the channel.txt file by deleting all content
    with open('channel.txt', 'w') as file:
        file.write('')
    update.message.reply_text("The channel.txt file has been reset.")
    update_channel_data_file()

