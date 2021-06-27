import json
import os
import time
import threading
import shutil

import googleapiclient
import requests
from os import path
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from googleapiclient.http import MediaFileUpload
from datetime import datetime

TMP_FOLDER_PATH = '/tmp1'
UNUSED_CREDENTIAL_PATH = 'unused'
UPLOADING_PATH = 'uploading'
SCOPES = ['https://www.googleapis.com/auth/drive']
CREDENTIAL_URL = 'http://35.226.69.158:16524/credential'


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
    json_response_obj = requests.get(CREDENTIAL_URL)
    if json_response_obj.status_code == 200:
        json_credential = json_response_obj.json().get('message').get('json_credential')
        return json_credential
    else:
        return False


def init_google_drive_credential():
    unused_credential = get_unused_credential()
    if unused_credential:
        creds = Credentials.from_authorized_user_info(unused_credential, SCOPES)
        service = build('drive', 'v3', credentials=creds)
        return service
    else:
        return None


def exception_occur_so_move_back_to_queue(file_name):
    shutil.move(os.path.join(UPLOADING_PATH, file_name), os.path.join(TMP_FOLDER_PATH, file_name))
    return True


def upload_file(file_name):
    google_drive = init_google_drive_credential()
    if google_drive:
        try:
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
                        is_upload_ok = True
                    if int(status.progress() * 100) % 5 == 0 and int(status.progress() * 100) != current_progress:
                        current_progress = int(status.progress() * 100)
                        print('[{}]: Upload file "{}" {}%'.format(datetime.now(), file_name,
                                                                  int(status.progress() * 100)))
            print('[{}]: Upload file "{}" completed'.format(datetime.now(), file_name))
            plot_file_obj.__del__()
            after_upload_success_delete_uploaded_file(file_name)
        except googleapiclient.errors.ResumableUploadError:
            exception_occur_so_move_back_to_queue(file_name)
    else:
        return


while True:
    if path.exists(TMP_FOLDER_PATH):
        print('[{}]: Checking folder path {}'.format(datetime.now(), TMP_FOLDER_PATH))
        for file in os.listdir(TMP_FOLDER_PATH):
            time.sleep(1)
            if file.endswith('.plot'):
                print('[{}]: Found file "{}"'.format(datetime.now(), file))
                upload_thread = threading.Thread(target=upload_file, args=[file])
                upload_thread.start()
                print('[{}]: Uploading process started for file "{}"'.format(datetime.now(), file))
