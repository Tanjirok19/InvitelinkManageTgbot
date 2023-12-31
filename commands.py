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
    # Clear the content of the channel.txt file by truncating it
    with open('channel.txt', 'w') as file:
        file.truncate(0)
    update.message.reply_text("The channel.txt file has been reset.")
    
    
def clear_command(update: Update, context: CallbackContext):
    # Read the channel.txt file
    with open('channel.txt', 'r') as file:
        channels = file.readlines()
    
    # Remove the revoked links from the channel.txt file
    updated_channels = [channel for channel in channels if 'revoked' not in channel]
    
    # Write the updated channel list back to the file
    with open('channel.txt', 'w') as file:
        file.writelines(updated_channels)
    
    update.message.reply_text("The revoked links have been cleared.")


