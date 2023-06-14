from flask import Flask, request
import time
import os
import telebot
from helper.account import account, cookie, retrieve_file_link

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
    response = f"User : {info['username']}\nSpace Used : {space}% of {space_max} GB\nPremium : {info['premium']}\nBandwidth Used : {bandwidth} GB\n\n\n"
    
    storage = account.listContents()
    folders = storage['folders']
    
    if folders:
        response+= "Folders - \n\n"
        for folder in folders:
            response+= f"{folder['fullname']}\n{round(folder['size']/(1024*1024),2)} MB\n\n"
    files = storage['files']
    if files:
        response+= "Files - \n\n"
        for file in files:
            response+= f"{file['name']}\n{round(file['size']/(1024*1024),2)} MB\n\n"
    
    bot.reply_to(message, response)

@bot.message_handler(func=lambda message: message.text.startswith('magnet:?xt='))
def handle_magnet(message):
    magnet = message.text
    add = account.addTorrent(magnetLink=magnet)
    if add['result'] == True:
        response = f"Torrent Added ({add['user_torrent_id']})\n\n{add['title']}\n\nTorrent hash : {add['torrent_hash']}"
        storage = account.listContents()
        torrents = storage['torrents']
        if torrents :
            for torrent in torrents:
                if torrent['warnings'] != '[]' and torrent['warnings'] :
                    result = account.deleteTorrent(torrentId=torrent['id'])
                    response = 'Defective Torrent.\n\n'
                    warnings = torrent['warnings'].strip('[]').replace('"','').split(',')
                    for warn in warnings:
                        response+= f"{warn}\n"
                else:
                    response+= f"\n\nQuality : {torrent['torrent_quality']}\n\n Size : {round(torrent['size'] / (1024 * 1024) , 2)} MB"
                    bot.reply_to(message, response)
                    while torrents :
                        torrents = account.listContents()['torrents']
                        bot.reply_to(message, "uwu")
                        time.sleep(4)
                    folders = account.listContents()['folders']
                    if folders:
                        for folder in folders:
                            folder_id = folder['id']
                    file_link = retrieve_file_link(cookie, folder_id)
                    delete = account.deleteFolder(folderId=folder_id)
                    if file_link:
                        bot.reply_to(message, f"File link: {file_link}")
                    else:
                        bot.reply_to(message, "Unable to retrieve file link.")
                    return
    else:
        response = f"Download failed \n\n{add['result']}"
    bot.reply_to(message, response)

@bot.message_handler(func=lambda message: message.text.startswith('http'))
def handle_scan_page(message):
    page = message.text
    scan = account.scanPage(page)
    torrents = scan['torrents']
    sep = '-'*30
    if scan['result'] == True and torrents :
        n = 0
        response = 'Torrents Found :\n\n\n'
        for torrent in torrents:
            n+=1
            new = f"{n}. {torrent['title']}\n\n{torrent['magnet']}\n\n{sep}\n\n"
            response+= new
            if len(response) > 3600:
                try:
                    bot.reply_to(message, response)
                    response = ''
                except:
                    response = response.replace(new, '*')
                    bot.reply_to(message, response)
                    response = new
        try:
            response+= f'{n} Torrents Found.'
            bot.reply_to(message, response)
        except:
            a = 1
    else:
        response = "No magnet links found."
        bot.reply_to(message, response)

@bot.message_handler(func=lambda message: True)
def handle_download(message):
    m = message.text
    bot.reply_to(message, m)



