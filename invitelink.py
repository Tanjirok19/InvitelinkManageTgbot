import telegram
import csv
import time
from telegram import ParseMode, Update
from telegram.ext import Updater, CommandHandler, CallbackContext

# Telegram Bot API token
TOKEN = '6267402462:AAHzWLlusljWq-8bdG2fraAl_dsuk05D730'

# Main channel ID where the bot will send the invite links
MAIN_CHANNEL_ID = '@aaokabh'

CHANNEL_DATA_FILE = 'channel.txt'

# Time interval in seconds (3 days = 259,200 seconds)
TIME_INTERVAL = 20

# Create a bot instance
bot = telegram.Bot(token=TOKEN)

# Store the message ID of the bot's previous message in the main channel
previous_message_id = None

# Store the time interval for the invite link management process
time_interval = TIME_INTERVAL

# Define an empty channel_data list
channel_data = []

with open('channel.txt', 'r') as file:
    reader = csv.reader(file)
    for row in reader:
        if row:
            channel_id = row[0]
            channel_name = row[1]
            additional_text = row[2]
            channel_entry = {'channel_id': channel_id, 'channel_name': channel_name, 'text': additional_text}
            channel_data.append(channel_entry)

#Update the CSV file
def update_channel_data_file():
    with open(CHANNEL_DATA_FILE, 'w') as file:
        writer = csv.writer(file)
        for channel in channel_data:
            writer.writerow([channel['channel_id'], channel['channel_name'], channel['text']])

        
def load_channel_data():
    channel_data = []
    try:
        with open(CHANNEL_DATA_FILE, 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                print(f"Processing row: {row}")
                if len(row) == 3:
                    channel_id = row[0]
                    channel_name = row[1]
                    additional_text = row[2]
                    channel_entry = {'channel_id': channel_id, 'channel_name': channel_name, 'text': additional_text}
                    channel_data.append(channel_entry)
                else:
                    print("Skipping row due to incorrect format")
    except FileNotFoundError:
        print(f"File '{CHANNEL_DATA_FILE}' not found.")
    return channel_data


# Generate an invite link for a channel
def generate_invite_link(channel_id):
    try:
        chat_invite_link = bot.export_chat_invite_link(chat_id=channel_id)
        if chat_invite_link:
            return chat_invite_link
    except telegram.TelegramError as e:
        print(f"Error generating invite link for channel {channel_id}: {e}")
    return None


# Create the message content with invite links and additional text
def create_message_content(channel_data):
    message_content = ""

    for channel in channel_data:
        channel_id = channel['channel_id']
        channel_name = channel['channel_name']
        additional_text = channel['text']

        invite_link = generate_invite_link(channel_id)

        if invite_link:
            message_content += f"<b>{channel_name}</b>:\n<a href='{invite_link}'>{invite_link}</a>\n{additional_text}\n\n"

    return message_content



# Send or edit the message in the main channel
def send_or_edit_main_channel_message(message_content):
    global previous_message_id

    if not message_content:
        print("Message content is empty. Aborting.")
        return

    print(f"Sending message content: {message_content}")

    if previous_message_id:
        bot.edit_message_text(chat_id=MAIN_CHANNEL_ID, message_id=previous_message_id, text=message_content, parse_mode=ParseMode.HTML)
    else:
        message = bot.send_message(chat_id=MAIN_CHANNEL_ID, text=message_content, parse_mode=ParseMode.HTML)
        previous_message_id = message.message_id


# Main function to manage the invite links
def manage_invite_links(context: CallbackContext):
    # Load the channel data
    channel_data = load_channel_data()

    # Create the message content
    message_content = create_message_content(channel_data)

    # Send or edit the message in the main channel
    send_or_edit_main_channel_message(message_content)

# Start the invite link management process
def start_management(update: Update, context: CallbackContext):
    if 'job' in context.chat_data:
        update.message.reply_text("Invite link management is already running.")
    else:
        job = context.job_queue.run_repeating(manage_invite_links, interval=time_interval, first=0, context=context)
        context.chat_data['job'] = job
        update.message.reply_text("Invite link management started successfully.")

# Stop the invite link management process
def stop_management(update: Update, context: CallbackContext):
    if 'job' in context.chat_data:
        job = context.chat_data['job']
        job.schedule_removal()
        del context.chat_data['job']
        update.message.reply_text("Invite link management stopped successfully.")
    else:
        update.message.reply_text("Invite link management is not running.")
        
# Set the time interval for the invite link management process
def set_time_interval(update: Update, context: CallbackContext):
    if len(context.args) == 0:
        update.message.reply_text("Please provide a time interval in seconds.")
    else:
        try:
            new_time_interval = int(context.args[0])
            global time_interval
            time_interval = new_time_interval
            update.message.reply_text(f"Time interval set to {new_time_interval} seconds.")
        except ValueError:
            update.message.reply_text("Invalid time interval. Please provide a valid integer.")
            
            
def add_channel(update: Update, context: CallbackContext):
    if len(context.args) < 4:
        update.message.reply_text(
            "Please provide the channel ID, channel name, additional text, and sticker.\n/addchannel <channel_id> <channel_name> <additional_text> <sticker>")
    else:
        channel_id = context.args[0]
        channel_name = context.args[1]
        additional_text = " ".join(context.args[2:-1])
        sticker = context.args[-1]

        channel = {'channel_id': channel_id, 'channel_name': channel_name, 'text': additional_text, 'sticker': sticker}
        channel_data.append(channel)

        update.message.reply_text(f"Channel {channel_name} added successfully.")

        update_channel_data_file()




def remove_channel(update: Update, context: CallbackContext):
    if len(context.args) < 1:
        update.message.reply_text("Please provide the channel ID.")
    else:
        channel_id = context.args[0]

        for channel in channel_data:
            if channel['channel_id'] == channel_id:
                channel_data.remove(channel)
                update.message.reply_text(f"Channel '{channel['channel_name']}' removed successfully.")
                update_channel_data_file()  # Update the channel data file
                return

        update.message.reply_text("Channel not found.")
           
        

def main():
    global channel_data
    channel_data = load_channel_data()
    # Create an Updater instance
    updater = Updater(token=TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # Add command handlers
    start_handler = CommandHandler('start', start_management)
    stop_handler = CommandHandler('stop', stop_management)
    set_interval_handler = CommandHandler('setinterval', set_time_interval)
    add_channel_handler = CommandHandler('addchannel', add_channel)
    remove_channel_handler = CommandHandler('removechannel', remove_channel)
    
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(stop_handler)
    dispatcher.add_handler(set_interval_handler)
    dispatcher.add_handler(add_channel_handler)
    dispatcher.add_handler(remove_channel_handler)


    # Start the bot
    updater.start_polling()
    print("Bot started.")

    # Run the bot until you press Ctrl-C
    updater.idle()

if __name__ == '__main__':
    main()
