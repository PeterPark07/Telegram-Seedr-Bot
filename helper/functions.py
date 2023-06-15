import requests
import json
import secrets
import wget


def retrieve_file_link(cookie, folder_id):
    # Retrieve the file link from the Seedr API for the specified folder ID
    data = {
        'folder_id': folder_id,
        'archive_arr[0][type]': 'folder',
        'archive_arr[0][id]': folder_id,
    }

    response = requests.put(f'https://www.seedr.cc/download/archive/init/2c94612b-ecc0-41f7-8892-{secrets.token_hex(6)}', cookies=json.loads(cookie), data=data).json()

    return response.get('url')


def download_file(url, output_name):
    # Download a file from the specified URL and save it with the given output name
    return wget.download(url, out=output_name)


def convert_size(size, unit):
    # Convert the given size to the specified unit
    units = {'MB': 1024 * 1024, 'GB': 1024 * 1024 * 1024}
    return round(size / units[unit], 2) if unit in units else size
