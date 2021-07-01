import os
import threading
import time

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

# Creating a public client app, Aquire a access token for the user and set the header for API calls
cognos_to_onedrive = msal.PublicClientApplication(CLIENT_ID, authority=AUTHORITY_URL)
print(cognos_to_onedrive)
token = cognos_to_onedrive.acquire_token_by_username_password(USERNAME, PASSWORD, SCOPES)
print(token)
headers = {'Authorization': 'Bearer {}'.format(token['access_token'])}
onedrive_destination = '{}/{}/me/drive/root:/'.format(RESOURCE_URL, API_VERSION)
cognos_reports_source = "needValidate"


def test(chunk, header, session):
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


# Looping through the files inside the source directory
for root, dirs, files in os.walk(cognos_reports_source):
    for file_name in files:
        file_path = os.path.join(root, file_name)
        file_size = os.stat(file_path).st_size
        file_data = open(file_path, 'rb')

        if file_size < 4100000:
            # Perform is simple upload to the API
            r = requests.put(onedrive_destination + "/" + file_name + ":/content", data=file_data, headers=headers)
        else:
            # Creating an upload session
            upload_session = requests.post(onedrive_destination + "/" + file_name + ":/createUploadSession",
                                           headers=headers).json()

            print(upload_session)

            with open(file_path, 'rb') as f:
                total_file_size = os.path.getsize(file_path)
                chunk_size = 1 * 1024 * 1024
                chunk_number = total_file_size // chunk_size
                chunk_leftover = total_file_size - chunk_size * chunk_number
                i = 1
                thread = None
                pool = []
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
                    thread = threading.Thread(target=test, args=[chunk_data, headers, upload_session])
                    thread.start()
                    pool.append(thread)
                    if len(pool) == 2:
                        pool[0].join()
                        pool = pool[1:]
                    time.sleep(0.5)
                    i = i + 1

        file_data.close()
