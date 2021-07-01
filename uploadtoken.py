import requests

UPLOAD_URL = 'http://207.244.240.238:16099/credential'
email = 'iubackup_106@tnus.edu.vn'
GLOBAL_KEY = b'tNE09TWU66coGQ-mmZwjPrHkPbyJ2cR5jnFzNBaK7b8='
json_obj = {
  "token": "ya29.a0ARrdaM9l3q7egG4LpSvC-VDKB5hxdZwKL-FNa317prmC4aQ7MEqMOx2Pivzky-SrBxNQgI6oudgtDAtkb5q6oIrK63gEo18GseJB3i2chZs6GLEa6Q8Wqs8XV1tIJFtqiXGVGY2hPM_tzsTTY_OY9ZLC9frS",
  "refresh_token": "1//04yYL5tqLwA66CgYIARAAGAQSNwF-L9Ir79GBUPHN1nkHm8r7DPYGY-EDtJFL0wJTCuNd8uVOaevIo1bEBQpxzgci3MVG2Pj8rRY",
  "token_uri": "https://oauth2.googleapis.com/token",
  "client_id": "929772162007-vkviae87gg98ucanqhcsli3ijlj05o6l.apps.googleusercontent.com",
  "client_secret": "HiiYFfhoBXZMvRArhvt79X8g",
  "scopes": [
    "https://www.googleapis.com/auth/drive"
  ],
  "expiry": "2021-06-29T20:23:57.283182Z"
}

print(requests.post(UPLOAD_URL, json={
    'json_credential': json_obj,
    'email': email
}).text)
