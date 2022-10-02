import os
import requests

amplitude_secret_key = '1795766d2d822cda9f4875654f9a6ee6'
amplitude_rec_id = 'xv8mseo'
user_id = '05087'

response = requests.get('https://profile-api.amplitude.com/v1/userprofile', 
    headers={'Authorization': f'Api-Key {amplitude_secret_key}'},
    params={'user_id': user_id, 'rec_id': amplitude_rec_id})

print(response.url)
print(response.content)