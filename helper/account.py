import os
from seedrcc import Login, Seedr

email = os.getenv('email')
password = os.getenv('pass')

seedr = Login(email, password)
response = seedr.authorize()

token = seedr.token
account = Seedr(token=token)

cookie = os.getenv('cookie')
cookie = '{"RSESS_remember": "' + cookie + '"}'