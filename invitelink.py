import csv
import telegram
import time
import codecs
import html
import emoji
import re
from telegram import ParseMode, Update
from telegram.ext import Updater, CommandHandler, CallbackContext,  Defaults
from commands import help_command, users_command, reset_command

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


def update_channel_data_file():
    with open(CHANNEL_DATA_FILE, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        for channel in channel_data:
            writer.writerow([
                channel['channel_id'],
                channel['channel_name'],
                channel['text']
            ])


def load_channel_data():
    channel_data = []
    try:
        with open(CHANNEL_DATA_FILE, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                print(f"Processing row: {row}")
                if len(row) == 3:
                    channel_id = row[0]
                    channel_name = html.unescape(row[1])  # Unescape HTML entities
                    additional_text = html.unescape(row[2])  # Unescape HTML entities
                    channel_entry = {'channel_id': channel_id, 'channel_name': channel_name, 'text': additional_text}
                    channel_data.append(channel_entry)
                else:
                    print("Skipping row due to incorrect format")
    except FileNotFoundError:
        print(f"File '{CHANNEL_DATA_FILE}' not found.")
    return channel_data


def generate_invite_link(channel_id):
    try:
        chat_invite_link = bot.export_chat_invite_link(chat_id=channel_id)
        if chat_invite_link:
            return chat_invite_link
    except telegram.TelegramError as e:
        print(f"Error generating invite link for channel {channel_id}: {e}")
    return None


def create_message_content(channel_data):
    message_content = ""

    for channel in channel_data:
        channel_id = channel['channel_id']
        channel_name = channel['channel_name']
        additional_text = channel['text']

        invite_link = generate_invite_link(channel_id)

        if invite_link:
            channel_name_emoji = emoji.demojize(channel_name)
            channel_entry = f"{channel_name_emoji}:\n{invite_link}\n{additional_text}\n\n"
            message_content += channel_entry

    return message_content


# Send or edit the message in the main channel
def send_or_edit_main_channel_message(message_content, message=None):
    global previous_message_id

    if not message_content:
        print("Message content is empty. Aborting.")
        return

    print(f"Sending message content: {message_content}")

    # Replace emoji placeholders with actual emojis
    message_content = emoji.emojize(message_content, use_aliases=True)

    if previous_message_id:
        bot.edit_message_text(chat_id=MAIN_CHANNEL_ID, message_id=previous_message_id, text=message_content, parse_mode=ParseMode.HTML, disable_web_page_preview=True)
    else:
        if message is not None:
            message = bot.send_message(chat_id=MAIN_CHANNEL_ID, text=message_content, parse_mode=ParseMode.HTML, disable_web_page_preview=True, reply_to_message_id=message.message_id)
        else:
            message = bot.send_message(chat_id=MAIN_CHANNEL_ID, text=message_content, parse_mode=ParseMode.HTML, disable_web_page_preview=True)
        previous_message_id = message.message_id




def manage_invite_links(context: CallbackContext):
    channel_data = load_channel_data()
    message_content = create_message_content(channel_data)
    send_or_edit_main_channel_message(message_content)


def start_management(update: Update, context: CallbackContext):
    if 'job' in context.chat_data:
        update.message.reply_text("Invite link management is already running.")
    else:
        job = context.job_queue.run_repeating(manage_invite_links, interval=time_interval, first=0, context=context)
        context.chat_data['job'] = job
        update.message.reply_text("<b>Invite link management started successfully.</b>")


def stop_management(update: Update, context: CallbackContext):
    if 'job' in context.chat_data:
        job = context.chat_data['job']
        job.schedule_removal()
        del context.chat_data['job']
        update.message.reply_text("Invite link management stopped successfully.")
    else:
        update.message.reply_text("Invite link management is not running.")


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
    if len(context.args) < 3:
        update.message.reply_text(
            "Please provide the channel ID, channel name, and additional text.\n/addchannel <channel_id> <channel_name> <additional_text>")
    else:
        channel_id = context.args[0]
        channel_name = context.args[1]
        additional_text = " ".join(context.args[2:])

        channel = {'channel_id': channel_id, 'channel_name': channel_name, 'text': additional_text}
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
                update.message.reply_text(f"<b>Channel '{channel['channel_name']}' removed successfully.</b>")
                update_channel_data_file()  # Update the channel data file
                return

        update.message.reply_text("Channel not found.")


def main():
    defaults = Defaults(parse_mode=ParseMode.HTML)
    global channel_data
    channel_data = load_channel_data()
    updater = Updater(token=TOKEN, use_context=True, defaults=defaults)
    dispatcher = updater.dispatcher

    start_handler = CommandHandler('start', start_management)
    stop_handler = CommandHandler('stop', stop_management)
    set_interval_handler = CommandHandler('setinterval', set_time_interval)
    add_channel_handler = CommandHandler('addchannel', add_channel)
    remove_channel_handler = CommandHandler('removechannel', remove_channel)
    reset_handler = CommandHandler('reset', reset_command)
    users_handler = CommandHandler('users', users_command)
    help_handler = CommandHandler('help', help_command)

    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(stop_handler)
    dispatcher.add_handler(set_interval_handler)
    dispatcher.add_handler(add_channel_handler)
    dispatcher.add_handler(remove_channel_handler)
    dispatcher.add_handler(help_handler)
    dispatcher.add_handler(users_handler)
    dispatcher.add_handler(reset_handler)

    updater.start_polling()
    print("Bot started.")

    updater.idle()


if __name__ == '__main__':
    main()
