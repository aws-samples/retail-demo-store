import os
import requests
import uuid
import time
import json

amplitude_secret_key = '1795766d2d822cda9f4875654f9a6ee6'
amplitude_rec_id = 'xv8mseo'

conversion = .2

control_group = []
experiment_group = []

output_file_name = 'src/aws-lambda/personalize-pre-create-resources/data/amplitude/conversion_events.json'

conversion_event = 'Purchase'

timestamp_start = time.time() # Start of script timestamp
first_timestamp = timestamp_start - (60*60*24*2)

def write_events(user_group):
    # Generate output file for experiment group
    time_increment = (60*60*24*2) / len(experiment_group)

    with open(output_file_name, 'w') as f:
        timestamp = first_timestamp
        for user in user_group:
            amplitude_event = {
                "event_type": conversion_event,
                "time": int(timestamp * 1000),  # Amplitude wants time in ms since the epoch, we have sec
                "user_id": user['user_id'],  # Amplitude wants a UID as a string with no less than 5 chars
                "insert_id": str(uuid.uuid4()),  # This is to prevent duplicates when re-running event gen scripts
                "event_properties": {
                    "product_id": user['items'][1],
                }
            }

            f.write(f'{json.dumps(amplitude_event)}\n')
            timestamp += time_increment

for user_id in range(1000, 2500):
    uid = f'{user_id:0>5}' 
    response = requests.get('https://profile-api.amplitude.com/v1/userprofile', 
        headers={'Authorization': f'Api-Key {amplitude_secret_key}'},
        params={'user_id': uid, 'rec_id': amplitude_rec_id})
    res = response.json()
    items = []
    is_user_in_control_group = True
    if res:
        for item in res['userData']['recommendations'][0]['items']:
            items.append(item)

        is_user_in_control_group = res['userData']['recommendations'][0]['is_control']

        if is_user_in_control_group:
            control_group.append({'user_id': uid, 'items': items})
        else:
            experiment_group.append({'user_id': uid, 'items': items})

    #print(f'{uid} {is_user_in_control_group}')

write_events(experiment_group)
# split the control list by half
half_length = int(len(control_group) / 2)
write_events(control_group[half_length:])
