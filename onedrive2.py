import requests
import json
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import MobileApplicationClient

client_id = '36b905fa-92d4-4672-852b-058d2873e9a0'
scopes = ['Sites.ReadWrite.All', 'Files.ReadWrite.All']
auth_url = 'https://login.microsoftonline.com/eff45447-476c-411c-993f-a4a62d97a2e6/oauth2/v2.0/authorize'

# OAuth2Session is an extension to requests.Session
# used to create an authorization url using the requests.Session interface
# MobileApplicationClient is used to get the Implicit Grant
oauth = OAuth2Session(client=MobileApplicationClient(client_id=client_id), scope=scopes)
authorization_url, state = oauth.authorization_url(auth_url)

consent_link = oauth.get(authorization_url)
print(consent_link.url)
