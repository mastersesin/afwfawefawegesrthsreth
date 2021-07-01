import os
import time
import threading

import requests
import json
import msal

# Configuration
CLIENT_ID = '36b905fa-92d4-4672-852b-058d2873e9a0'
TENANT_ID = 'eff45447-476c-411c-993f-a4a62d97a2e6'
AUTHORITY_URL = 'https://login.microsoftonline.com/{}'.format(TENANT_ID)
RESOURCE_URL = 'https://graph.microsoft.com/'
API_VERSION = 'v1.0'
USERNAME = 'tytran@nolivocorp.onmicrosoft.com'  # Office365 user's account username
PASSWORD = 'Ckiuzk4ever!@#'
SCOPES = ['Sites.ReadWrite.All', 'Files.ReadWrite.All']  # Add other scopes/permissions as needed.
UPLOAD_PATH = 'needValidate'
FILE_NAME = 'chia_plot'

# Creating a public client app, Aquire a access token for the user and set the header for API calls
cognos_to_onedrive = msal.PublicClientApplication(CLIENT_ID, authority=AUTHORITY_URL)
print(cognos_to_onedrive)
token = cognos_to_onedrive.acquire_token_by_username_password(USERNAME, PASSWORD, SCOPES)
print(token)
headers = {'Authorization': 'Bearer {}'.format(token['access_token'])}
onedrive_destination = '{}/{}/me/drive/root:/'.format(RESOURCE_URL, API_VERSION)


def file_chunk(max_chunk=1 * 1024 * 1024, path=None):
    file_size = os.path.getsize(path)
    amount_bytes_whole = file_size // max_chunk
    amount_bytes_part = file_size % thread_count
    upload_range = []
    for i in range(thread_count):
        upload_range.append([i * amount_bytes_whole, amount_bytes_whole * (i + 1) - 1])
    upload_range[thread_count - 1][1] += amount_bytes_part
    return upload_range


def upload_file(session):
    total_file_size = os.path.getsize(os.path.join(UPLOAD_PATH, FILE_NAME))
    with open(os.path.join(UPLOAD_PATH, FILE_NAME), 'rb') as f:
        split_range = file_split(2, os.path.join(UPLOAD_PATH, FILE_NAME))
        start_byte, end_byte = split_range[0]
        while True:
            # f.seek(current_byte)
            print(f.read(1))
            # chunk_data = f.read(chunk_size)
            # print(chunk_data)
            # start_index = i * chunk_size
            # end_index = start_index + chunk_size
            # # If end of file, break
            # if not chunk_data:
            #     break
            # if i == chunk_number:
            #     end_index = start_index + chunk_leftover
            # # Setting the header with the appropriate chunk data location in the file
            # headers_upload = {'Content-Length': '{}'.format(chunk_size),
            #                   'Content-Range': 'bytes {}-{}/{}'.format(start_index, end_index - 1, end_byte)}
            # # Upload one chunk at a time
            # chunk_data_upload = requests.put(session['uploadUrl'], data=chunk_data, headers=headers_upload)
            # print(chunk_data_upload)
            # print(chunk_data_upload.json())
            # i = i + 1


headers_upload_session = {'Authorization': 'Bearer {}'.format(token['access_token'])}
upload_session = requests.post(onedrive_destination + "/" + FILE_NAME + ":/createUploadSession",
                               headers=headers_upload_session).json()
upload_file(upload_session)

# file_path = 'needValidate/chia_plot'
# with open(file_path, 'rb') as f:
#     total_file_size = os.path.getsize(file_path)
#     total_thread = 4
#     print(total_file_size // 4)
#     thread_upload_start_stop_bytes = []
#     chunk_size = 1 * 1024 * 1024
#     chunk_number = total_file_size // chunk_size
#     print(chunk_number)
#     chunk_leftover = total_file_size - chunk_size * chunk_number
#     f.close()
