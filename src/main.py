from flask import Flask, request
import time
import os
import telebot
from helper.account import account

app = Flask(__name__)
bot = telebot.TeleBot(os.getenv('seedr_bot'), threaded=False)
bot.set_webhook(url = getenv('url'))
state = str(account.testToken())

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
    bot.reply_to(message, f"Hello {name}!Welcome to SEEDR Bot\n\n If you want to see the available commands, type /help.\nBot active : {state}")

@bot.message_handler(func=lambda message: True)
def handle_download(message):
    m = message.text
    bot.reply_to(message, m)



