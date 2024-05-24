import boto3

pinpoint_client = boto3.client("pinpoint")
pinpoint_app_id = "YOUR_PINPOINT_APP_ID"

def send_pinpoint_message(phone_number):
    send_message_address = {
        phone_number: {
            "ChannelType": "SMS"
        }
    }
    send_message_input = {
        "ApplicationId": pinpoint_app_id,
        "MessageRequest": {
            "Addresses": send_message_address,
            "MessageConfiguration": {
                "SMSMessage": {
                    "Body": "Reply Y to receive one time automated marketing messages at this number. No purchase necessary. T&C apply.",
                    "MessageType": "TRANSACTIONAL"
                }
            }
        }
    }
    pinpoint_client.send_messages(MessageRequest=send_message_input)
