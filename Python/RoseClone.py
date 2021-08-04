# %%
import os
import logging
import pandas as pd
import telebot
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from telethon import TelegramClient
from datetime import datetime, timedelta
from time import sleep
from pyTelegramBotCAPTCHA import CaptchaManager
from getInfo import getInfo
from getChart import getChart
from dotenv import load_dotenv
load_dotenv()
# %%
logger = telebot.logger
telebot.logger.setLevel(logging.DEBUG)

scheduler = AsyncIOScheduler()
scheduler.daemonize = True

bot = telebot.TeleBot(os.getenv('TELE_KEY'),
                      parse_mode=None, skip_pending=True)
captcha_manager = CaptchaManager(bot.get_me().id, default_timeout=90)
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
client = TelegramClient(os.getenv('TELE_PHONE'), api_id=os.getenv(
    'TELE_APP_ID'), api_hash=os.getenv('TELE_APP_HASH'), loop=loop)
client.connect()
if not client.is_user_authorized():
    client.send_code_request(os.getenv('TELE_PHONE'))
    client.sign_in(os.getenv('TELE_PHONE', input('Enter Code:')))
client.start()

members = {}

all_participants = client.iter_participants(
    os.getenv('TELE_CHAT'), aggressive=True)
for participants in all_participants:
    members[participants.username] = participants.id

bot.set_my_commands([
    telebot.types.BotCommand("/start", "Start This Bitch - creator"),
    telebot.types.BotCommand("/help", "Hopefully Does Just That - all"),
    telebot.types.BotCommand("/welcome", 'Shows Current Welcome - admin'),
    telebot.types.BotCommand("/setwelcome", 'Set New Welcome - admin'),
    telebot.types.BotCommand(
        '/enableprice', 'Start Display of Market Data - creator'),
    telebot.types.BotCommand('/chart', 'Displays Current 2hr Chart - all'),
    telebot.types.BotCommand('/create', 'Create New Command - admin'),
    telebot.types.BotCommand('/delete', 'Delete Old Command - admin'),
    telebot.types.BotCommand(
        '/commands', "Lists All Current Custom Commands - all"),
    telebot.types.BotCommand('/muteall', 'Mute Entire Chat - admin'),
    telebot.types.BotCommand('/unmuteall', 'Unmute Entire Chat - admin'),
    telebot.types.BotCommand('/warn', 'Tally a Warning for Member - admin'),
    telebot.types.BotCommand('/ban', 'Same as /warn - admin'),
    telebot.types.BotCommand('/admin', "@'s All Admins - all"),
    telebot.types.BotCommand('/report', 'Reports Member to All Admins - all'),
    telebot.types.BotCommand(
        '/watchlist', 'Displays All Offenders and Warnings - admin'),
    telebot.types.BotCommand('/restrict', 'Restrict Member - admin'),
    telebot.types.BotCommand('/unrestrict', 'Unrestrict Member - admin')

])


symbol = ""  # "Arigato"
contract = ""  # "0x5Cfec8aC17D7f4489942e5E3264B233d8E69AeFC"
burn_address = []  # ["0x0000000000000000000000000000000000000000", "0x0000000000000000000000000000000000000001"]
welcome_msg = 'Put A Welcome Here'
chat_id = ''
price_enabled = False
admins = []
god = ['BDBB13']
bot_enabled = False
bot_messages = []
watchlist = {}
url_whitelist = []
dynamic_commands = pd.DataFrame(columns=['command', 'content', 'file', 'type'])

# I guess I need a fucking start command


@bot.message_handler(commands=['start'])
def start_bot(message):
    global bot_enabled
    if (message.from_user.username in god) and not bot_enabled:
        global chat_id
        chat_id = message.chat.id
        scheduler.start()
        scheduler.add_job(send_price, 'interval', minutes=10)
        scheduler.add_job(get_chart, 'interval', minutes=5)
        scheduler.add_job(update_admins, 'interval', seconds=15)
        update_admins()
        bot_enabled = True
        sent_message = bot.send_message(
            chat_id=chat_id, text="*Hello Creator!*\n_Please Set a Welcome_\nUse /help if you need it!", parse_mode="MARKDOWN")
        asyncio.run(clean_up_message(sent_message.id, 15))


async def clean_up_message(message_id, sleep):
    await asyncio.sleep(sleep)
    bot.delete_message(chat_id=chat_id, message_id=message_id)


@bot.message_handler(commands=['help'])
def send_help(message):
    markup = telebot.types.InlineKeyboardMarkup()
    button_mod = telebot.types.InlineKeyboardButton(
        'Mod Commands', callback_data=f'?mod{message.from_user.id}')
    button_creator = telebot.types.InlineKeyboardButton(
        'Creator Commands', callback_data=f'?creator{message.from_user.id}')
    button_common = telebot.types.InlineKeyboardButton(
        'Common Commands', callback_data=f'?common{message.from_user.id}')
    button_format = telebot.types.InlineKeyboardButton(
        'Format Help', callback_data=f'?format{message.from_user.id}')
    button_done = telebot.types.InlineKeyboardButton(
        'Done', callback_data=f'?done{message.from_user.id}')
    markup.add(button_creator, button_mod)
    markup.add(button_common, button_format)
    markup.add(button_done)
    bot.send_message(
        chat_id=message.chat.id, text=("This is the help section!\nPlease feel free to select a category and explore my commands!"), reply_to_message_id=message.id, reply_markup=markup)


# Done help menu

def help_done_query(callback):
    if callback.data == f'?done{callback.message.reply_to_message.from_user.id}':
        bot.delete_message(
            chat_id=callback.message.chat.id, message_id=callback.message.id)


# Home help menu


@bot.callback_query_handler(func=lambda call: call.data.startswith('?home'))
def help_home_query(callback):
    if callback.data == f'?home{callback.message.reply_to_message.from_user.id}':
        markup = telebot.types.InlineKeyboardMarkup()
        button_mod = telebot.types.InlineKeyboardButton(
            'Mod Commands', callback_data=f'?mod{callback.message.reply_to_message.from_user.id}')
        button_creator = telebot.types.InlineKeyboardButton(
            'Creator Commands', callback_data=f'?creator{callback.message.reply_to_message.from_user.id}')
        button_common = telebot.types.InlineKeyboardButton(
            'Common Commands', callback_data=f'?common{callback.message.reply_to_message.from_user.id}')
        button_format = telebot.types.InlineKeyboardButton(
            'Format Help', callback_data=f'?format{callback.message.reply_to_message.from_user.id}')
        button_done = telebot.types.InlineKeyboardButton(
            'Done', callback_data=f'?done{callback.message.reply_to_message.from_user.id}')
        markup.add(button_creator, button_mod)
        markup.add(button_common, button_format)
        markup.add(button_done)
        bot.edit_message_text(
            chat_id=callback.message.chat.id, message_id=callback.message.id, text="This is the help section!\nPlease feel free to select a category and explore my commands!", reply_markup=markup)


# Common commands help menu


@bot.callback_query_handler(func=lambda call: call.data.startswith('?common'))
def help_common_query(callback):
    if callback.data == f'?common{callback.message.reply_to_message.from_user.id}':
        markup = telebot.types.InlineKeyboardMarkup()
        button_back = telebot.types.InlineKeyboardButton(
            'Back', callback_data=f'?home{callback.message.reply_to_message.from_user.id}')
        markup.add(button_back)
        bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.id,
                              text=("``` /help``` - well you are here...\n"
                                    "``` /admin <@offender>, /report<@offender>``` - will send one message with all admins mentioned can reply or mention specific username\n"
                                    "``` /commands``` - will list all current commands as keywords without the '/'"), parse_mode='MARKDOWN', reply_markup=markup)


# Creator commands help menu

@bot.callback_query_handler(func=lambda call: call.data.startswith('?creator'))
def help_creator_query(callback):
    if callback.data == f'?creator{callback.message.reply_to_message.from_user.id}':
        markup = telebot.types.InlineKeyboardMarkup()
        button_back = telebot.types.InlineKeyboardButton(
            'Back', callback_data=f'?home{callback.message.reply_to_message.from_user.id}')
        markup.add(button_back)
        bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.id,
                              text=("``` /start```- Activates bots functionality past just the help function\n"
                                    "``` /enableprice``` - Enables the chart command and price displayed every 10 min"), parse_mode='MARKDOWN', reply_markup=markup)


# Format help menu

@bot.callback_query_handler(func=lambda call: call.data.startswith('?format'))
def help_format_query(callback):
    if callback.data == f'?format{callback.message.reply_to_message.from_user.id}':
        markup = telebot.types.InlineKeyboardMarkup()
        button_back = telebot.types.InlineKeyboardButton(
            'Back', callback_data=f'?home{callback.message.reply_to_message.from_user.id}')
        markup.add(button_back)
        bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.id,
                              text=("Markdown Formatting\n"
                                    "You can format your message using bold, italics, underline, and much more. Go ahead and experiment!\n"
                                    "Supported markdown:\n"
                                    "-``` \`code words\````: Backticks are used for monospace fonts. Shows as: code words.\n"
                                    "-``` _italic words_```: Underscores are used for italic fonts. Shows as: italic words.\n"
                                    "-``` *bold words*```: Asterisks are used for bold fonts. Shows as: bold words.\n"
                                    "-``` ~strikethrough~```: Tildes are used for strikethrough. Shows as: strikethrough.\n"
                                    "-``` __underline__```: Double underscores are used for underlines. Shows as: underline. NOTE: Some clients try to be smart and interpret it as italic. In that case, try to use your app's built-in formatting.\n"
                                    "-``` [hyperlink](google.com)```: This is the formatting used for hyperlinks.\n"), parse_mode='MARKDOWNV2', reply_markup=markup)


# Mod commands help menu


@bot.callback_query_handler(func=lambda call: call.data.startswith('?mod'))
def help_mod_query(callback):
    if callback.data == f'?mod{callback.message.reply_to_message.from_user.id}':
        markup = telebot.types.InlineKeyboardMarkup()
        button_back = telebot.types.InlineKeyboardButton(
            'Back', callback_data=f'?home{callback.message.reply_to_message.from_user.id}')
        markup.add(button_back)
        bot.edit_message_text(chat_id=callback.message.chat.id,
                              message_id=callback.message.id,
                              text=("``` /welcome <noformat>``` : will display current welcome message - suffix with noformat to display without markdown formatting\n"
                                    "``` /setwelcome <string of text>``` : will set welcome to whatever string of text follows and will format with markdown\n"
                                    "``` /muteall, /unmuteall``` - does just that! changes permissions of entire chat\n"
                                    "``` /warn <@offender>, /ban <@offender>``` - can either be a reply or can have username next to command tally one warning for user then bans after 3 warnings\n"
                                    "``` /restrict <@offender>, /unrestrict <@offender>``` - does just that! can either be a reply or can have username next to command\n"
                                    "``` /create <command> <content>``` - will create a new dynamic command can either be text or videos/photos using the caption\n"
                                    "``` /delete <command>``` - will delete the command and content from the database"),
                              parse_mode='MARKDOWN', reply_markup=markup)


# Message handler for new chat members


@bot.message_handler(content_types=["new_chat_members"])
def new_member(message):
    global members
    new_user_id = message.json.get("new_chat_member").get("id")
    new_user = bot.get_chat_member(message.chat.id, new_user_id).user
    members[new_user.username] = new_user.id
    if bot_enabled:
        captcha_manager.restrict_chat_member(bot,
                                             message.chat.id, new_user.id)
        markup = telebot.types.InlineKeyboardMarkup()
        button_verify = telebot.types.InlineKeyboardButton(
            'Human', callback_data=f'verified')
        markup.add(button_verify)
        sent_message = bot.send_message(
            chat_id=message.chat.id, text='_Select Your Species To Gain Access_', reply_markup=markup, parse_mode='MARKDOWN')
        asyncio.run(clean_up_message(sent_message.id, 30))

# Unrestrict new chat members


@bot.callback_query_handler(func=lambda call: call.data == 'verified')
def captcha_query(callback):
    captcha_manager.unrestrict_chat_member(bot,
                                           callback.message.chat.id, callback.from_user.id)
    sent_message = bot.send_message(chat_id=callback.message.chat.id,
                                    text=welcome_msg, parse_mode='MARKDOWN')
    asyncio.run(clean_up_message(sent_message.id, 30))


# Set and view welcome in markdown or un-formatted


@bot.message_handler(commands=['welcome'])
def send_welcome(message):
    if (message.from_user.username in admins) and bot_enabled:
        if 'noformat' in message.text:
            sent_message = bot.send_message(chat_id=message.chat.id,
                                            text=welcome_msg, parse_mode=None)
            asyncio.run(clean_up_message(sent_message.id, 60))
        else:
            sent_message = bot.send_message(chat_id=message.chat.id, text=welcome_msg,
                                            parse_mode='MARKDOWN')
            asyncio.run(clean_up_message(sent_message.id, 60))
    else:
        sent_message = bot.send_message(chat_id=message.chat.id,
                                        text='_You Cannot Do That!_', parse_mode='MARKDOWN')
        asyncio.run(clean_up_message(sent_message.id, 15))


@bot.message_handler(commands=['setwelcome'])
def set_welcome(message):
    if (message.from_user.username in admins) and bot_enabled:
        global welcome_msg
        welcome_msg = message.text.split()[1:]
        welcome_msg = ' '.join(welcome_msg)
        sent_message = bot.send_message(chat_id=message.chat.id,
                                        text=welcome_msg, parse_mode='MARKDOWN')
        asyncio.run(clean_up_message(sent_message.id, 60))
    else:
        sent_message = bot.send_message(chat_id=message.chat.id,
                                        text='_You Cannot Do That!_', parse_mode='MARKDOWN')
        asyncio.run(clean_up_message(sent_message.id, 15))


# Function for schedule to send token info

def send_price():
    if price_enabled:
        price, market_cap, holders, total_supply, burn_supply = getInfo(
            contract, burn_address)
        string = (f"**Token:** ```{symbol}```\n"
                  f"**Contract:** ```{contract}```\n"
                  f"**Price: ${price: .7f}\n"
                  f"Market Cap: ${int(market_cap):,}\n"
                  f"Holders: {holders:,}\n"
                  f"Total Supply: {int(total_supply):,} {symbol}\n"
                  f"Supply Burnt: {int(burn_supply):,} {symbol}**")
        bot.send_message(chat_id=chat_id, text=string, parse_mode='MARKDOWN')


def get_chart():
    if price_enabled:
        getChart()

# Enable price retrieval


@bot.message_handler(commands=['enableprice'])
def enable_price(message):
    if (message.from_user.username in god) and bot_enabled:
        global price_enabled, symbol, contract, burn_address
        msg_arr = message.text.split()
        price_enabled = True
        symbol = msg_arr[1]
        contract = msg_arr[2]
        for wallet in msg_arr[3:]:
            burn_address.append(wallet)
        send_price()
        get_chart()
        sent_message = bot.send_message(chat_id=message.chat.id,
                                        text='*Price Has Been Enabled!*', parse_mode='MARKDOWN')
        asyncio.run(clean_up_message(sent_message.id, 15))
    else:
        sent_message = bot.send_message(chat_id=message.chat.id,
                                        text='_You Cannot Do That!_', parse_mode='MARKDOWN')
        asyncio.run(clean_up_message(sent_message.id, 15))


# Send chart as PNG


@bot.message_handler(commands=['chart'])
def send_chart(message):
    if price_enabled:
        with open('Images/chart.png', 'rb') as photo:
            bot.send_photo(chat_id=chat_id, photo=photo)
            photo.close()
    else:
        sent_message = bot.send_message(
            chat_id=chat_id, text='_Contract Not Released!_', parse_mode='MARKDOWN')
        asyncio.run(clean_up_message(sent_message.id, 15))


# Update list of admins for privlege check


def update_admins():
    global admins
    admins = []
    for admin in bot.get_chat_administrators(chat_id):
        admins.append(admin.user.username)


# Dynamic commands

# Create a text echo

@bot.message_handler(commands=['create'], content_types=['text'])
def create_command_text(message):
    if (message.from_user.username in admins) and bot_enabled:
        global dynamic_commands
        msg_arr = message.text.split()
        if not msg_arr[1:]:
            sent_message = bot.send_message(
                chat_id=chat_id, text=f"No information was given", parse_mode='MARKDOWN')
            asyncio.run(clean_up_message(sent_message.id, 15))
        else:
            command = msg_arr[1][1:]
            if msg_arr[1][0] != '/':
                sent_message = bot.send_message(
                    chat_id=chat_id, text=f"Commands must start with a '/'", parse_mode='MARKDOWN')
                asyncio.run(clean_up_message(sent_message.id, 15))
            elif command in dynamic_commands['command'].values:
                sent_message = bot.send_message(
                    chat_id=chat_id, text=f" ```{command}``` already exists!", parse_mode='MARKDOWN')
                asyncio.run(clean_up_message(sent_message.id, 15))
            else:
                content = ' '.join(msg_arr[2:])
                if not content.split():
                    sent_message = bot.send_message(
                        chat_id=chat_id, text=f"_You Need To Add Content!_", parse_mode='MARKDOWN')
                    asyncio.run(clean_up_message(sent_message.id, 15))
                else:
                    dynamic_commands = dynamic_commands.append(pd.DataFrame(
                        {'command': [command], 'content': [content], 'file': None, 'type': ['text']}), ignore_index=True)
                    sent_message = bot.send_message(
                        chat_id=chat_id, text=f"Command ```{command}``` was created!", parse_mode='MARKDOWN')
                    asyncio.run(clean_up_message(sent_message.id, 15))


# Create a image echo

@bot.message_handler(func=lambda msg: msg.caption.split()[0] == '/create', content_types=['photo'])
def create_command_img(message):
    if (message.from_user.username in admins) and bot_enabled:
        global dynamic_commands
        msg_arr = message.caption.split()
        if not msg_arr[1:]:
            sent_message = bot.send_message(
                chat_id=chat_id, text=f"No information was given", parse_mode='MARKDOWN')
            asyncio.run(clean_up_message(sent_message.id, 15))
        else:
            command = msg_arr[1][1:]
            if msg_arr[1][0] != '/':
                sent_message = bot.send_message(
                    chat_id=chat_id, text=f"Commands must start with a '/'", parse_mode='MARKDOWN')
                asyncio.run(clean_up_message(sent_message.id, 15))
            elif command in dynamic_commands['command'].values:
                sent_message = bot.send_message(
                    chat_id=chat_id, text=f" ```{command}``` already exists!", parse_mode='MARKDOWN')
                asyncio.run(clean_up_message(sent_message.id, 15))
            else:
                fileID = message.photo[-1].file_id
                file_info = bot.get_file(fileID)
                downloaded_file = bot.download_file(file_info.file_path)
                file_name = f'Data/{message.caption.split()[1]}.jpg'
                with open(file_name, 'wb') as photo:
                    photo.write(downloaded_file)
                    photo.close()

                content = ' '.join(msg_arr[2:])
                dynamic_commands = dynamic_commands.append(pd.DataFrame(
                    {'command': [command], 'content': [content], 'file': file_name, 'type': ['photo']}), ignore_index=True)
                sent_message = bot.send_message(
                    chat_id=chat_id, text=f"Command ```{command}``` was created!", parse_mode='MARKDOWN')
                asyncio.run(clean_up_message(sent_message.id, 15))

# Create a video echo


@bot.message_handler(func=lambda msg: msg.caption.split()[0] == '/create', content_types=['animation'])
def create__command_video(message):
    if (message.from_user.username in admins) and bot_enabled:
        global dynamic_commands
        msg_arr = message.caption.split()
        if not msg_arr[1:]:
            sent_message = bot.send_message(
                chat_id=chat_id, text=f"No information was given", parse_mode='MARKDOWN')
            asyncio.run(clean_up_message(sent_message.id, 15))
        else:
            command = msg_arr[1][1:]
            if msg_arr[1][0] != '/':
                sent_message = bot.send_message(
                    chat_id=chat_id, text=f"Commands must start with a '/'", parse_mode='MARKDOWN')
                asyncio.run(clean_up_message(sent_message.id, 15))
            elif command in dynamic_commands['command'].values:
                sent_message = bot.send_message(
                    chat_id=chat_id, text=f" ```{command}``` already exists!", parse_mode='MARKDOWN')
                asyncio.run(clean_up_message(sent_message.id, 15))
            else:
                fileID = message.animation.file_id
                file_info = bot.get_file(fileID)
                downloaded_file = bot.download_file(file_info.file_path)
                file_name = f'Data/{message.caption.split()[1]}.mp4'
                with open(file_name, 'wb') as photo:
                    photo.write(downloaded_file)
                    photo.close()

                content = ' '.join(msg_arr[2:])
                dynamic_commands = dynamic_commands.append(pd.DataFrame(
                    {'command': [command], 'content': [content], 'file': file_name, 'type': ['video']}), ignore_index=True)
                sent_message = bot.send_message(
                    chat_id=chat_id, text=f"Command ```{command}``` was created!", parse_mode='MARKDOWN')
                asyncio.run(clean_up_message(sent_message.id, 15))

# Delete a command


@bot.message_handler(commands=['delete'])
def delete_command(message):
    if (message.from_user.username in admins) and bot_enabled:
        global dynamic_commands
        if not message.text.split()[1:]:
            sent_message = bot.send_message(
                chat_id=chat_id, text=f"No information was given", parse_mode='MARKDOWN')
            asyncio.run(clean_up_message(sent_message.id, 15))
        else:
            command = message.text.split()[1][1:]
            if command in dynamic_commands['command'].values:
                dynamic_commands = dynamic_commands.set_index('command')
                if dynamic_commands.loc[command]['file'] is not None:
                    os.remove(dynamic_commands.loc[command]['file'])
                dynamic_commands = dynamic_commands.drop(
                    command, axis=0)
                dynamic_commands = dynamic_commands.reset_index()
                sent_message = bot.send_message(
                    chat_id=chat_id, text=f" ```{command}``` has been deleted!", parse_mode='MARKDOWN')
                asyncio.run(clean_up_message(sent_message.id, 15))
            else:
                sent_message = bot.send_message(
                    chat_id=chat_id, text=f" ```{command}``` doesn't exist!", parse_mode='MARKDOWN')
                asyncio.run(clean_up_message(sent_message.id, 15))


# Handle commands


@bot.message_handler(func=lambda msg: msg.text[0] == '/' and (msg.text.split()[0][1:] in dynamic_commands['command'].to_list()))
def call_dynamic_command(message):
    if bot_enabled:
        global dynamic_commands
        new_df = dynamic_commands
        new_df = new_df.set_index('command')
        command = message.text.split()[0][1:]
        if new_df.loc[command]['type'] == 'text':
            if 'noformat' in message.text.split():
                bot.send_message(
                    chat_id=chat_id, text=new_df.loc[command]['content'], parse_mode=None)
            else:
                bot.send_message(
                    chat_id=chat_id, text=new_df.loc[command]['content'], parse_mode='MARKDOWN')
        elif new_df.loc[command]['type'] == 'photo':
            with open(new_df.loc[command]['file'], 'rb') as photo:
                if 'noformat' in message.text.split():
                    bot.send_photo(chat_id=chat_id, photo=photo, caption=(
                        " " if not new_df.loc[command]['content'] else new_df.loc[command]['content']), parse_mode=None)
                else:
                    bot.send_photo(chat_id=chat_id, photo=photo, caption=(
                        " " if not new_df.loc[command]['content'] else new_df.loc[command]['content']), parse_mode='MARKDOWN')
                photo.close()
        elif new_df.loc[command]['type'] == 'video':
            with open(new_df.loc[command]['file'], 'rb') as video:
                if 'noformat' in message.text.split():
                    bot.send_animation(chat_id=chat_id, animation=video, caption=(
                        " " if not new_df.loc[command]['content'] else new_df.loc[command]['content']), parse_mode=None)
                else:
                    bot.send_animation(chat_id=chat_id, animation=video, caption=(
                        " " if not new_df.loc[command]['content'] else new_df.loc[command]['content']), parse_mode='MARKDOWN')
                video.close()


# Print list of dynamic commands


@bot.message_handler(commands=['commands'])
def show_commands(message):
    global dynamic_commands
    if dynamic_commands.empty:
        sent_message = bot.send_message(
            chat_id=chat_id, text=f"Use ```create``` to make a command!", parse_mode='MARKDOWN')
        asyncio.run(clean_up_message(sent_message.id, 15))
    else:
        string = ''
        for command in dynamic_commands['command']:
            string += f"```{command}```\n"
        bot.send_message(chat_id=chat_id, text=string, parse_mode='MARKDOWN')

# Mod commands

# Mute and unmute chat


@bot.message_handler(commands=['muteall'])
def mute_all(message):
    if (message.from_user.username in admins) and bot_enabled:
        bot.set_chat_permissions(
            chat_id=chat_id, permissions=telebot.types.ChatPermissions(can_send_messages=False))
        bot.send_message(chat_id=message.chat.id,
                         text='_Chat Has Been Muted_', parse_mode='MARKDOWN')
    else:
        sent_message = bot.send_message(chat_id=message.chat.id,
                                        text='_You Cannot Do That!_', parse_mode='MARKDOWN')
        asyncio.run(clean_up_message(sent_message.id, 15))


@bot.message_handler(commands=['unmuteall'])
def mute_all(message):
    if (message.from_user.username in admins) and bot_enabled:
        bot.set_chat_permissions(chat_id=chat_id, permissions=telebot.types.ChatPermissions(
            can_send_messages=True, can_add_web_page_previews=True, can_send_other_messages=True, can_invite_users=True, can_send_media_messages=True))
        bot.send_message(chat_id=message.chat.id,
                         text='_Chat Has Been Unmuted_', parse_mode='MARKDOWN')
    else:
        sent_message = bot.send_message(chat_id=message.chat.id,
                                        text='_You Cannot Do That!_', parse_mode='MARKDOWN')
        asyncio.run(clean_up_message(sent_message.id, 15))


# Ban/warn/kick members

@bot.message_handler(commands=['warn', 'ban'])
def warn_user(message):
    if (message.from_user.username in admins) and bot_enabled:
        global members
        try:
            offender = message.reply_to_message.from_user.username
        except:
            offender = message.text.split()[1][1:]
        if offender not in members:
            sent_message = bot.send_message(
                chat_id=chat_id, text=f"{offender} isn't in this chat!", parse_mode="MARKDOWN")
            asyncio.run(clean_up_message(sent_message.id, 15))
        elif offender in admins:
            sent_message = bot.send_message(
                chat_id=chat_id, text=f"{offender} is an admin", parse_mode="MARKDOWN")
            asyncio.run(clean_up_message(sent_message.id, 15))
        else:
            if offender not in watchlist:
                watchlist[offender] = 1
            else:
                watchlist[offender] += 1
            sent_message = bot.send_message(
                chat_id=chat_id, text=f"{offender} has been warned {watchlist[offender]} time(s)", parse_mode="MARKDOWN")
            asyncio.run(clean_up_message(sent_message.id, 60))
            if watchlist[offender] >= 3:
                date_unban = datetime.now() + timedelta(days=15)
                bot.kick_chat_member(
                    chat_id=chat_id, user_id=members[offender], until_date=date_unban)
                sent_message = bot.send_message(
                    chat_id=chat_id, text=f"{offender} has been banned until {date_unban.date}")
                asyncio.run(clean_up_message(sent_message.id, 60))


# Unban member

@bot.message_handler(commands=['unban'])
def ban_user(message):
    if (message.from_user.username in admins) and bot_enabled:
        global members
        try:
            offender = message.reply_to_message.from_user.username
        except:
            offender = message.text.split()[1][1:]
        bot.unban_chat_member(chat_id=chat_id, )


# Restrict and unrestrict users

@bot.message_handler(commands=['restrict'])
def restrict_user(message):
    if (message.from_user.username in admins) and bot_enabled:
        global members
        try:
            offender = message.reply_to_message.from_user
            if offender.username in admins:
                sent_message = bot.send_message(
                    chat_id=chat_id, text=f'{offender.username} is an admin')
                asyncio.run(clean_up_message(sent_message.id, 15))
            elif offender.username not in members.keys():
                sent_message = bot.send_message(
                    chat_id=chat_id, text=f'{offender.username} is not a member')
                asyncio.run(clean_up_message(sent_message.id, 15))
            else:
                captcha_manager.restrict_chat_member(
                    bot, message.chat.id, offender.id)
                sent_message = bot.send_message(
                    chat_id=chat_id, text=f"{offender.username} has been restricted")
                asyncio.run(clean_up_message(sent_message.id, 60))
        except:
            if not message.text.split()[1:]:
                sent_message = bot.send_message(
                    chat_id=chat_id, text=f'Specify a member')
                asyncio.run(clean_up_message(sent_message.id, 15))
            else:
                username = message.text.split()[1][1:]
                if username in admins:
                    sent_message = bot.send_message(
                        chat_id=chat_id, text=f'{username} is an admin')
                    asyncio.run(clean_up_message(sent_message.id, 15))
                elif username not in members.keys():
                    sent_message = bot.send_message(
                        chat_id=chat_id, text=f'{username} is not a member')
                    asyncio.run(clean_up_message(sent_message.id, 15))
                else:
                    offender = bot.get_chat_member(
                        chat_id=chat_id, user_id=members[username]).user
                    captcha_manager.restrict_chat_member(
                        bot, message.chat.id, offender.id)
                    sent_message = bot.send_message(
                        chat_id=chat_id, text=f"{username} has been restricted")
                    asyncio.run(clean_up_message(sent_message.id, 15))


@bot.message_handler(commands=['unrestrict'])
def unrestrict_user(message):
    if (message.from_user.username in admins) and bot_enabled:
        try:
            offender = message.reply_to_message.from_user
            if offender.username in admins:
                sent_message = bot.send_message(
                    chat_id=chat_id, text=f'{offender.username} is an admin')
                asyncio.run(clean_up_message(sent_message.id, 15))
            elif offender.username not in members.keys():
                sent_message = bot.send_message(
                    chat_id=chat_id, text=f'{offender.username} is not a member')
                asyncio.run(clean_up_message(sent_message.id, 15))
            else:
                captcha_manager.unrestrict_chat_member(
                    bot, message.chat.id, offender.id)
                sent_message = bot.send_message(
                    chat_id=chat_id, text=f"{offender.username}'s restriction has been lifted!")
                asyncio.run(clean_up_message(sent_message.id, 60))
        except:
            if not message.text.split()[1:]:
                sent_message = bot.send_message(
                    chat_id=chat_id, text=f'Specify a member')
                asyncio.run(clean_up_message(sent_message.id, 15))
            else:
                username = message.text.split()[1][1:]
                if username in admins:
                    sent_message = bot.send_message(
                        chat_id=chat_id, text=f'{username} is an admin')
                    asyncio.run(clean_up_message(sent_message.id, 15))
                elif username not in members.keys():
                    sent_message = bot.send_message(
                        chat_id=chat_id, text=f'{username} is not a member')
                    asyncio.run(clean_up_message(sent_message.id, 15))
                else:
                    offender = bot.get_chat_member(
                        chat_id=chat_id, user_id=members[username]).user
                    captcha_manager.unrestrict_chat_member(
                        bot, message.chat.id, offender.id)
                    sent_message = bot.send_message(
                        chat_id=chat_id, text=f"{username}'s restriction has been lifted!")
                    asyncio.run(clean_up_message(sent_message.id, 60))

# Report to admins


@bot.message_handler(commands=['admin', 'report'])
def report_user(message):
    if bot_enabled:
        string = ""
        try:
            offender = message.reply_to_message.from_user.username
            string += f'@{offender} has been reported\n\n'
            for admin in admins:
                string += f"@{admin} "
            bot.send_message(chat_id=chat_id, text=string)
        except:
            if not message.text.split()[1:]:
                for admin in admins:
                    string += f"@{admin} "
                bot.send_message(chat_id=chat_id, text=string)
            else:
                offender = message.text.split()[1][1:]
                string += f'@{offender} has been reported\n\n'
                for admin in admins:
                    string += f"@{admin} "
                bot.send_message(chat_id=chat_id, text=string)

# Naughty List


@bot.message_handler(commands=['watchlist'])
def get_watchlist(message):
    if (message.from_user.username in admins) and bot_enabled:
        if watchlist.empty():
            string = "*Everyone Is Behaving*"
        else:
            string = ""
            for offender, warnings in watchlist.items():
                string += f"{offender}: {warnings} warning(s)\n"
        bot.send_message(chat_id=chat_id, text=string,
                         parse_mode="MARKDOWN", timeout=5)


async def is_url(message):
    if message.text.split() not in url_whitelist:
        for entity in message.entities:
            if entity.type == "url":
                return True


@bot.message_handler(func=lambda message: message.entities and asyncio.run(is_url(message)))
def delete_url(message):
    if bot_enabled and message.from_user.username not in admins:
        bot.delete_message(chat_id=message.chat.id, message_id=message.id)


bot.polling()

# %%
