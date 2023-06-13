from flask import Flask, request
import time
import os
import telebot
from helper.account import account

app = Flask(__name__)
bot = telebot.TeleBot(os.getenv('seedr_bot'), threaded=False)
state = str(account.testToken()['result'])

# Bot route to handle incoming messages
@app.route('/', methods=['POST'])
def telegram():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return 'OK', 200

# Command: /start
@bot.message_handler(commands=['start'])
def handle_start(message):
    # Handle the /start command
    name =  message.from_user.username or message.from_user.first_name or message.from_user.last_name
    bot.reply_to(message, f"Hello {name}! Welcome to Torrent Bot\n\n If you want to see the available commands, type /help.\nBot active : {state}")

# Command: /help
@bot.message_handler(commands=['help'])
def handle_help(message):
    # Handle the /help command
    bot.reply_to(message, "Available commands:\n\n/start\n/help\n/info")

# Command: /info
@bot.message_handler(commands=['info'])
def handle_account_info(message):
    # Handle the /info command
    info = account.getSettings()['account']
    response = ''
    space = round(info['space_used'] / info['space_max'], 4)*100
    bandwidth = info['bandwidth_used'] / (1024 * 1024)
    response+= f"User : {info['username']}\nSpace Used : {space}\nPremium : {info['premium']}\nBandwidth Used : {bandwidth}"


    bot.reply_to(message, response)

@bot.message_handler(func=lambda message: True)
def handle_download(message):
    m = message.text
    bot.reply_to(message, m)



