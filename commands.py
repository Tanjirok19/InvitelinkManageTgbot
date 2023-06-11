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
    # Open the channel.txt file
    with open('channel.txt', 'r') as file:
        channels = file.readlines()

    # Clear the file by deleting all content
    with open('channel.txt', 'w') as file:
        file.write('')

    # Send a reply indicating that the file has been reset
    update.message.reply_text("The channel.txt file has been reset.")

    # Optionally, you can also send a message for each deleted channel
    for channel in channels:
        channel = channel.strip()  # Remove leading/trailing whitespaces
        update.message.reply_text(f"Deleted channel: {channel}")

        # Alternatively, if you don't want to update the text file, you can skip this part
        # and only send the message for each deleted channel without removing them from the file


