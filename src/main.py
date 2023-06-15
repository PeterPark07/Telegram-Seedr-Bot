from flask import Flask, request
import os
import time
import telebot
from helper.account import account, cookie
from helper.functions import retrieve_file_link, download_file, convert_size
import gofile

app = Flask(__name__)
bot = telebot.TeleBot(os.getenv('seedr_bot'), threaded=False)
state = str(account.testToken()['result'])
last_message_id = []


@app.route('/', methods=['POST'])
def telegram():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return 'OK', 200


@bot.message_handler(commands=['start'])
def handle_start(message):
    name = message.from_user.username or message.from_user.first_name or message.from_user.last_name
    welcome_message = f"Hello {name}!\nWelcome to Torrent Bot\n\nIf you want to see the available commands, type /help.\nBot Active: {state}"
    bot.reply_to(message, welcome_message)


@bot.message_handler(commands=['help'])
def handle_help(message):
    help_message = "Available commands:\n\n" \
                   "/start - Start the bot\n" \
                   "/help - Display available commands\n" \
                   "/info - Get account information"
    bot.reply_to(message, help_message)


@bot.message_handler(commands=['info'])
def handle_account_info(message):
    account_info = account.getSettings()['account']
    space_used = account_info['space_used']
    space_max = account_info['space_max']
    bandwidth_used = account_info['bandwidth_used']
    username = account_info['username']
    premium = account_info['premium']

    space_percentage = round(space_used / space_max * 100, 2)
    bandwidth_gb = convert_size(bandwidth_used, 'GB')

    response = f"User: {username}\n" \
               f"Space Used: {space_percentage}% of {convert_size(space_max, 'GB')} GB\n" \
               f"Premium: {premium}\n" \
               f"Bandwidth Used: {bandwidth_gb} GB\n\n"

    storage = account.listContents()
    folders = storage.get('folders', [])
    files = storage.get('files', [])

    if folders:
        folder_info = '\n\n'.join([f"{folder['fullname']}\n{convert_size(folder['size'], 'MB')} MB" for folder in folders])
        response += "Folders - \n\n" + folder_info

    if files:
        file_info = '\n\n'.join([f"{file['name']}\n{convert_size(file['size'], 'MB')} MB" for file in files])
        response += "Files - \n\n" + file_info

    bot.reply_to(message, response)

@bot.message_handler(func=lambda message: message.text.startswith('http'))
def handle_scan_page(message):
    # Check if the message has already been processed
    global last_message_id
    if message.message_id in last_message_id:
        return
    last_message_id.append(message.message_id)
    
    page = message.text
    bot.reply_to(message, 'Scanning Page...')
    scan = account.scanPage(page)
    torrents = scan['torrents']
    sep = '-' * 30

    if scan['result'] == True and torrents:
        response = 'Torrents Found:\n\n\n'
        for n, torrent in enumerate(torrents, start=1):
            new = f"{n}. {torrent['title']}\n\n{torrent['magnet']}\n\n{sep}\n\n"
            if len(response + new) > 3900:
                bot.reply_to(message, response)
                response = new
            else:
                response += new

        response += f'{n} Torrents Found.'
        bot.reply_to(message, response) if response else None
    else:
        response = "No magnet links found."
        bot.reply_to(message, response)





@bot.message_handler(func=lambda message: message.text.startswith('magnet:?xt='))
def handle_magnet(message):
    global last_message_id

    # Check if the message has already been processed
    if message.message_id in last_message_id:
        return
    last_message_id.append(message.message_id)

    magnet = message.text
    # Add the torrent using the provided magnet link
    add = account.addTorrent(magnetLink=magnet)
    
    if add['result'] == True:
        response = f"Torrent Added ({add['user_torrent_id']})\n\n{add['title']}\n\nTorrent hash: {add['torrent_hash']}"

        # Retrieve storage information
        storage = account.listContents()
        torrents = storage['torrents']

        for torrent in torrents:
            if torrent['warnings'] != '[]' and torrent['warnings']:
                # Delete defective torrents
                result = account.deleteTorrent(torrentId=torrent['id'])
                response = 'Defective Torrent.\n\n'
                warnings = torrent['warnings'].strip('[]').replace('"', '').split(',')
                for warn in warnings:
                    response += f"{warn}\n"
            else:
                response += f"\n\nQuality: {torrent['torrent_quality']}\n\nSize: {convert_size(torrent['size'], 'MB')} MB"
                bot.reply_to(message, response)
                while torrents:
                    time.sleep(10)
                    torrents = account.listContents()['torrents']
                
                folders = account.listContents()['folders']
                
                if folders:
                    for folder in folders:
                        folder_id = folder['id']
                
                file_link = retrieve_file_link(cookie, folder_id)
                file_name = torrent['name'] + '.zip'

                try:
                    bot.reply_to(message, f"Downloading...")
                    downloaded = download_file(file_link, file_name)
                    bot.reply_to(message, f"Downloaded : {downloaded}")
                except Exception as e:
                    bot.reply_to(message, f"Not downloaded.\n{e}")
                    delete = account.deleteFolder(folderId=folder_id)
                    return

                delete = account.deleteFolder(folderId=folder_id)
                
                try:
                    bot.reply_to(message, "Uploading..." )
                    response = gofile.uploadFile(file=file_name)
                    bot.reply_to(message, "Uploaded." )
                except:
                    bot.reply_to(message, "Not Uploaded." )
                return
    else:
        response = f"Download failed\n\n{add['result']}"
    bot.reply_to(message, response)




@bot.message_handler(func=lambda message: True)
def handle_other_messages(message):
    m = message.text
    bot.reply_to(message, m)
