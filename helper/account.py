import seedrcc
from seedrcc import Login
from seedrcc import Seedr
import requests
import json
import secrets
import os
import wget

email = os.getenv('email')
password = os.getenv('pass')

seedr = Login(email, password)
response = seedr.authorize()

token = seedr.token
account = Seedr(token=token)
cookie = os.getenv('cookie')
cookie = '{"RSESS_remember": "' + cookie + '"}'


def retrieve_file_link(cookie, folder_id):
    data = {
        'folder_id': folder_id,
        'archive_arr[0][type]': 'folder',
        'archive_arr[0][id]': folder_id,
    }

    cookies = json.loads(cookie)

    response = requests.put(f'https://www.seedr.cc/download/archive/init/2c94612b-ecc0-41f7-8892-{secrets.token_hex(6)}', cookies=cookies, data=data).json()

    if 'url' in response:
        return response['url']
    else:
        return None
        
        
def download(url, name):
    wget.download(url, out=name)