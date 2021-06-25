from __future__ import print_function
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from cryptography.fernet import Fernet

import json, os

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive']


def main():
    """Shows basic usage of the Drive v3 API.
    Prints the names and ids of the first 10 files the user has access to.
    """
    global_key = b'tNE09TWU66coGQ-mmZwjPrHkPbyJ2cR5jnFzNBaK7b8='
    creds = None
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        list_file = os.listdir()
        for file in list_file:
            if 'code_secret_client' in file or 'client_secret' in file:
                flow = InstalledAppFlow.from_client_secrets_file(
                    file, SCOPES)
                creds = flow.run_local_server(port=0)
                break

    # Save the credentials for the next run
    with open('token.{}.json'.format(json.loads(creds.to_json())['client_id']), 'w') as token:
        f = Fernet(global_key)
        token.write(f.encrypt(creds.to_json().encode()).decode())


if __name__ == '__main__':
    main()
