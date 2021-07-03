import json
import os
import subprocess
import time
import threading
import shutil
import urllib.request
import logging
import random

import googleapiclient
import requests
from os import path
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from googleapiclient.http import MediaFileUpload
from datetime import datetime

logging.basicConfig(filename='log.txt',
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG)
TMP_FOLDER_PATH = '/tmp2'
CURRENT_PATH = os.getcwd()
UNUSED_CREDENTIAL_PATH = 'unused'
UPLOADING_PATH = 'uploading'
SCOPES = ['https://www.googleapis.com/auth/drive']
CREDENTIAL_URL = 'http://207.244.240.238:16099/credential'
LOG_URL = 'http://207.244.240.238:16099/log'


def move_file_to_uploading(file_name):
    shutil.move(os.path.join(TMP_FOLDER_PATH, file_name), os.path.join(CURRENT_PATH, UPLOADING_PATH, file_name))
    return True


def after_upload_success_delete_uploaded_file(file_name):
    os.remove(os.path.join(CURRENT_PATH, UPLOADING_PATH, file_name))


def post_log(file_name, email):
    data = json.loads(urllib.request.urlopen("http://ip.jsontest.com/").read())
    ip = data.get('ip', 'Error')
    requests.post(LOG_URL, json={'ip': ip, 'file_name': file_name, 'email': email})


def get_unused_credential():
    json_response_obj = requests.get(CREDENTIAL_URL)
    if json_response_obj.status_code == 200:
        json_credential = json_response_obj.json().get('message').get('json_credential')
        email = json_response_obj.json().get('message').get('email')
        return json_credential, email
    else:
        return None, None


def init_google_drive_credential():
    unused_credential, email = get_unused_credential()
    if unused_credential:
        creds = Credentials.from_authorized_user_info(unused_credential, SCOPES)
        service = build('drive', 'v3', credentials=creds)
        return service, email
    else:
        return None, None


def exception_occur_so_move_back_to_queue(file_name, reason):
    logging.error(
        'Exception occur so move "{}" back from {} to {} \n {}'.format(file_name, UPLOADING_PATH, TMP_FOLDER_PATH,
                                                                       reason))
    shutil.move(os.path.join(CURRENT_PATH, UPLOADING_PATH, file_name), os.path.join(TMP_FOLDER_PATH, file_name))
    return True


def upload_file(file_name):
    google_drive, email = init_google_drive_credential()
    if google_drive:
        try:
            plot_file_obj = MediaFileUpload(os.path.join(CURRENT_PATH, UPLOADING_PATH, file_name),
                                            chunksize=256 * 1024 * 1024,
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
            post_log(file_name, email)
            after_upload_success_delete_uploaded_file(file_name)
        except googleapiclient.errors.ResumableUploadError as e:
            exception_occur_so_move_back_to_queue(file_name, e)
        except Exception as e:
            print(e)
            exception_occur_so_move_back_to_queue(file_name, e)
    else:
        exception_occur_so_move_back_to_queue(file_name, 'dont know')
        time.sleep(10)
        return


while True:
    time.sleep(5)
    out = subprocess.Popen(['sudo', 'pidof', 'chia_plot'],
                           stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT)
    stdout, stderr = out.communicate()
    if not stdout:
        if random.randint(0, 1) == 0:
            cmd = 'sudo rm -rf /mnt/ramdisk1/*'
            os.system(cmd)
            cmd = 'chia_plot -t /tmp1/tmp1/ -d /tmp1/ -2 /mnt/ramdisk1/ -n 1 -r 32 -p a94a9f827a062a24d8f8c2201f9113fd8428da53deded15d501d8c94ed59e7d700b44bdc7e0e42a1501426fccca005b6 -f ac99a1d74615b16d12189e2b82a51e0640ca1aa38c55a5841f78c58ac448972555585c8295c181a0eaf6a6d9bf5f5d2d'
            os.system(cmd)
        else:
            cmd = 'sudo rm -rf /mnt/ramdisk1/*'
            os.system(cmd)
            cmd = 'chia_plot -t /tmp2/tmp2/ -d /tmp2/ -2 /mnt/ramdisk1/ -n 1 -r 32 -p a59e33b8108631810978bb60e9150ff9b4f38ad2e76776d8491acb7e7dacb906f9fff90ee6dcff9ca56d54ea20702f92 -f ad1b159147734d8a817e776e02ef0ced0ff61db9d6695c24bf7147a6622082c9ab59620697e9c434accdf3ab76bd1393'
            os.system(cmd)
    if path.exists(TMP_FOLDER_PATH):
        print('[{}]: Checking folder path {}'.format(datetime.now(), TMP_FOLDER_PATH))
        for file in os.listdir(TMP_FOLDER_PATH):
            time.sleep(1)
            if file.endswith('.plot'):
                move_file_to_uploading(file)
                print('[{}]: Found file "{}"'.format(datetime.now(), file))
                upload_thread = threading.Thread(target=upload_file, args=[file])
                upload_thread.start()
                print('[{}]: Uploading process started for file "{}"'.format(datetime.now(), file))
