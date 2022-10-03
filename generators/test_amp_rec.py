import os
import requests

amplitude_secret_key = '1795766d2d822cda9f4875654f9a6ee6'
amplitude_rec_id = 'xv8mseo'
#user_id = 5087

for user_id in range(1, 25):
    uid = f'{user_id:0>5}' 
    response = requests.get('https://profile-api.amplitude.com/v1/userprofile', 
        headers={'Authorization': f'Api-Key {amplitude_secret_key}'},
        params={'user_id': uid, 'rec_id': amplitude_rec_id})
    res = response.json()
    items = []
    is_user_in_control_group = True
    if res:
        for item in res['userData']['recommendations'][0]['items']:
            items.append({'itemId': item})

        is_user_in_control_group = res['userData']['recommendations'][0]['is_control']

    print(f'{uid} {is_user_in_control_group}')