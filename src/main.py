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
    space = round(info['space_used'] / info['space_max'] * 100, 2)
    space_max = info['space_max'] / (1024 * 1024 * 1024)
    bandwidth = round(info['bandwidth_used'] / (1024 * 1024 * 1024), 2)
    response = f"User : {info['username']}\nSpace Used : {space}% of {space_max} GB\nPremium : {info['premium']}\nBandwidth Used : {bandwidth} GB"

    bot.reply_to(message, response)

@bot.message_handler(func=lambda message: message.text.startswith('magnet:?xt='))
def handle_magnet(message):
    magnet = message.text
    add = account.addTorrent(magnetLink=magnet)
    if add['result'] == True:
        response = f"Torrent Added ({add['user_torrent_id']})\n\n{add['title']}\n\nTorrent hash : {add['torrent_hash']}"
    else:
        response = f"Download failed \n\n{add['result']}"
    bot.reply_to(message, response)

@bot.message_handler(func=lambda message: message.text.startswith('http'))
def handle_scan_page(message):
    page = message.text
    scan = account.scanPage(page)
    if scan['result'] == True and scan['torrents'] != [] :
        if len(scan['torrents']) < 20:
            n = 0
            response = 'Torrents Found :\n\n\n'
            for torrent in scan['torrents']:
                n+=1
                response+= f"{n}. {torrent['title']}\n\n{torrent['magnet']}\n\n\n"
        else:
            response = "The page contains too many links!!"
    else:
        response = "No magnet links found."
    bot.reply_to(message, response)

@bot.message_handler(func=lambda message: True)
def handle_download(message):
    m = message.text
    bot.reply_to(message, m)



