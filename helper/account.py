import seedrcc
from seedrcc import Login
from seedrcc import Seedr
import os

email = os.getenv('email')
password = os.getenv('pass')

seedr = Login(email, password)
response = seedr.authorize()

token = seedr.token
account = Seedr(token=token)
cookie = os.getenv('cookie')
cookie = '{"RSESS_remember": "' + cookie + '"}'
