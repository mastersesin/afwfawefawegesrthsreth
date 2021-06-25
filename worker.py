import json
import os
import time
import threading
import shutil
from os import path
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from googleapiclient.http import MediaFileUpload
from datetime import datetime
from cryptography.fernet import Fernet

TMP_FOLDER_PATH = '/tmp1'
TMP_FOLDER_PATH_2 = '/tmp2'
UNUSED_CREDENTIAL_PATH = 'unused'
UPLOADING_PATH = 'uploading'
SCOPES = ['https://www.googleapis.com/auth/drive']


def edit_json_token_file(file_name, json_obj):
    json_file_obj = open(os.path.join(UNUSED_CREDENTIAL_PATH, file_name), 'w')
    json_file_obj.write(json.dumps(json_obj))
    json_file_obj.close()
    return True


def move_file_to_uploading(file_name):
    shutil.move(os.path.join(TMP_FOLDER_PATH, file_name), os.path.join(UPLOADING_PATH, file_name))
    return True


def uploading_so_update_used_times_and_utc(file_name):
    json_file_obj = open(os.path.join(UNUSED_CREDENTIAL_PATH, file_name))
    json_obj = json.load(json_file_obj)
    json_obj['last_used_utc'] = int(time.time())
    json_obj['used_times'] += 1
    edit_json_token_file(file_name, json_obj)


def after_upload_success_delete_uploaded_file(file_name):
    os.remove(os.path.join(UPLOADING_PATH, file_name))


def get_unused_credential():
    GLOBAL_KEY = b'tNE09TWU66coGQ-mmZwjPrHkPbyJ2cR5jnFzNBaK7b8='
    GLOBAL_ENCRYPTION_WORKER = Fernet(GLOBAL_KEY)
    try:
        for file_name in os.listdir(UNUSED_CREDENTIAL_PATH):
            encrypted_json_obj = open(os.path.join(UNUSED_CREDENTIAL_PATH, file_name)).read()
            try:
                json_obj = json.loads(GLOBAL_ENCRYPTION_WORKER.decrypt(encrypted_json_obj.encode()).decode())
            except Exception as e:
                json_obj = json.loads(encrypted_json_obj)
            if 'last_used_utc' in json_obj and 'used_times' in json_obj:
                if json_obj['used_times'] >= 7 and json_obj['last_used_utc'] - int(time.time()) <= 86400:
                    continue
                elif json_obj['used_times'] >= 7 and json_obj['last_used_utc'] - int(time.time()) > 86400:
                    json_obj['last_used_utc'] = 0
                    json_obj['used_times'] = 0
            else:
                json_obj['last_used_utc'] = 0
                json_obj['used_times'] = 0
                edit_json_token_file(file_name, json_obj)
            return file_name
        print('Application need more credential file')
        os.abort()
    except IndexError:
        return None


def init_google_drive_credential():
    unused_credential = get_unused_credential()
    if unused_credential:
        unused_credential_path_final = os.path.join(UNUSED_CREDENTIAL_PATH, unused_credential)
        creds = Credentials.from_authorized_user_file(unused_credential_path_final, SCOPES)
        service = build('drive', 'v3', credentials=creds)
        return service, unused_credential
    else:
        print('Error in getting credential')
        os.abort()


def upload_file(file_name):
    google_drive, credential_file = init_google_drive_credential()
    move_file_to_uploading(file_name)
    plot_file_obj = MediaFileUpload(os.path.join(UPLOADING_PATH, file_name), chunksize=100 * 1024 * 1024,
                                    resumable=True)
    file_metadata = {
        'name': file_name
    }
    request = google_drive.files().create(media_body=plot_file_obj, body=file_metadata)
    response = None
    is_upload_ok = False
    current_progress = 0
    while response is None:
        status, response = request.next_chunk()
        if status:
            if not is_upload_ok:
                uploading_so_update_used_times_and_utc(credential_file)
                is_upload_ok = True
            if int(status.progress() * 100) % 5 == 0 and int(status.progress() * 100) != current_progress:
                current_progress = int(status.progress() * 100)
                print('[{}]: Upload file "{}" {}%'.format(datetime.now(), file_name, int(status.progress() * 100)))
    print('[{}]: Upload file "{}" completed'.format(datetime.now(), file_name))
    plot_file_obj.__del__()
    after_upload_success_delete_uploaded_file(file_name)


while True:
    if path.exists(TMP_FOLDER_PATH):
        print('[{}]: Checking folder path {}'.format(datetime.now(), TMP_FOLDER_PATH))
        for file in os.listdir(TMP_FOLDER_PATH):
            time.sleep(5)
            if file.endswith('.plot'):
                print('[{}]: Found file "{}"'.format(datetime.now(), file))
                upload_thread = threading.Thread(target=upload_file, args=[file])
                upload_thread.start()
                print('[{}]: Uploading process started for file "{}"'.format(datetime.now(), file))
    time.sleep(5)
    if path.exists(TMP_FOLDER_PATH_2):
        print('[{}]: Checking folder path {}'.format(datetime.now(), TMP_FOLDER_PATH_2))
        for file in os.listdir(TMP_FOLDER_PATH_2):
            time.sleep(5)
            if file.endswith('.plot'):
                print('[{}]: Found file "{}"'.format(datetime.now(), file))
                upload_thread = threading.Thread(target=upload_file, args=[file])
                upload_thread.start()
                print('[{}]: Uploading process started for file "{}"'.format(datetime.now(), file))
    time.sleep(30)
