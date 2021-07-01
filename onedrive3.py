import json
import os
import time
import threading
import shutil
import urllib.request
import msal

import googleapiclient
import requests
from os import path
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from googleapiclient.http import MediaFileUpload
from datetime import datetime

# Configuration
CLIENT_ID = '36b905fa-92d4-4672-852b-058d2873e9a0'
TENANT_ID = 'eff45447-476c-411c-993f-a4a62d97a2e6'
AUTHORITY_URL = 'https://login.microsoftonline.com/{}'.format(TENANT_ID)
RESOURCE_URL = 'https://graph.microsoft.com/'
API_VERSION = 'v1.0'
USERNAME = 'tytran@nolivocorp.onmicrosoft.com'  # Office365 user's account username
PASSWORD = 'Ckiuzk4ever!@#'
SCOPES = ['Sites.ReadWrite.All', 'Files.ReadWrite.All']  # Add other scopes/permissions as needed.

# TMP_FOLDER_PATH = '/tmp1'
TMP_FOLDER_PATH = 'needValidate'
UPLOADING_PATH = 'uploading'
# CREDENTIAL_URL = 'http://207.244.240.238:16099/credential'
# LOG_URL = 'http://207.244.240.238:16099/log'


def create_public_client(file_name):
    # Creating a public client app, Aquire a access token for the user and set the header for API calls
    cognos_to_onedrive = msal.PublicClientApplication(CLIENT_ID, authority=AUTHORITY_URL)
    token = cognos_to_onedrive.acquire_token_by_username_password(USERNAME, PASSWORD, SCOPES)
    print(token)
    headers = {'Authorization': 'Bearer {}'.format(token['access_token'])}
    onedrive_destination = '{}/{}/me/drive/root:/'.format(RESOURCE_URL, API_VERSION)
    upload_session = requests.post(onedrive_destination + "/" + file_name + ":/createUploadSession",
                                   headers=headers).json()
    return upload_session


def move_file_to_uploading(file_name):
    shutil.move(os.path.join(TMP_FOLDER_PATH, file_name), os.path.join(UPLOADING_PATH, file_name))
    return True


def make_put_api_call(chunk, header, session):
    while True:
        time.sleep(0.5)
        try:
            chunk_data_upload = requests.put(session['uploadUrl'], data=chunk, headers=header)
            print(chunk_data_upload.status_code not in [200, 201, 202])
            print(chunk_data_upload.json())
            if chunk_data_upload.status_code not in [200, 201, 202]:
                raise Exception('Cannot update yet')
            break
        except Exception as e:
            print(e)
            continue


def start_upload(session, file_name):
    with open(os.path.join(UPLOADING_PATH, file), 'rb') as f:
        total_file_size = os.path.getsize(file_name)
        chunk_size = 250 * 1024 * 1024
        chunk_number = total_file_size // chunk_size
        chunk_leftover = total_file_size - chunk_size * chunk_number
        i = 1
        thread = None
        while True:
            chunk_data = f.read(chunk_size)
            start_index = i * chunk_size
            end_index = start_index + chunk_size
            # If end of file, break
            if not chunk_data:
                break
            if i == chunk_number:
                end_index = start_index + chunk_leftover + 1
            # Setting the header with the appropriate chunk data location in the file
            headers = {'Content-Length': '{}'.format(chunk_size),
                       'Content-Range': 'bytes {}-/{}'.format(start_index, end_index - 1, total_file_size)}
            print(start_index, end_index - 1, total_file_size)
            # Upload one chunk at a time
            if thread:
                thread.start()
                thread.join()
            thread = threading.Thread(target=make_put_api_call, args=[chunk_data, headers, session])
            time.sleep(0.5)
            i = i + 1


def after_upload_success_delete_uploaded_file(file_name):
    os.remove(os.path.join(UPLOADING_PATH, file_name))


def post_log(file_name, email):
    data = json.loads(urllib.request.urlopen("http://ip.jsontest.com/").read())
    ip = data.get('ip', 'Error')
    requests.post(LOG_URL, json={'ip': ip, 'file_name': file_name, 'email': email})


def exception_occur_so_move_back_to_queue(file_name):
    print('Exception occur so move "{}" back from {} to {}'.format(file_name, UPLOADING_PATH, TMP_FOLDER_PATH))
    shutil.move(os.path.join(UPLOADING_PATH, file_name), os.path.join(TMP_FOLDER_PATH, file_name))
    return True


def upload_file(file_name):
    onedrive = create_public_client(file_name)
    if onedrive and onedrive.get('uploadUrl'):
        try:
            start_upload(onedrive, file_name)
            post_log(file_name, USERNAME)
            after_upload_success_delete_uploaded_file(file_name)
        except Exception as e:
            print(e)
            exception_occur_so_move_back_to_queue(file_name)
    else:
        exception_occur_so_move_back_to_queue(file_name)
        time.sleep(10)
        return


while True:
    time.sleep(1)
    if path.exists(TMP_FOLDER_PATH):
        print('[{}]: Checking folder path {}'.format(datetime.now(), TMP_FOLDER_PATH))
        for file in os.listdir(TMP_FOLDER_PATH):
            time.sleep(1)
            # if file.endswith('.plot'):
            if file == 'chia_plot':
                move_file_to_uploading(file)
                print('[{}]: Found file "{}"'.format(datetime.now(), file))
                upload_thread = threading.Thread(target=upload_file, args=[file])
                upload_thread.start()
                print('[{}]: Uploading process started for file "{}"'.format(datetime.now(), file))
