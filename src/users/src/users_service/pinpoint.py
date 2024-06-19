import boto3
import os
from flask import Flask, current_app
from botocore.exceptions import ClientError


class Pinpoint():
    def __init__(self, app: Flask | None = None) -> None:
        if app is not None:
            self.init_app(app)
            
    def init_app(self, app: Flask) -> None:
        client = boto3.client("pinpoint", region_name=app.config.get("AWS_DEFAULT_REGION"))
        self.pinpoint_app_id = app.config.get("PINPOINT_APP_ID")
        self.client = client


    def send_pinpoint_message(self, phone_number):
        send_message_address = {
            phone_number: {
                "ChannelType": "SMS"
            }
        }
        send_message_input = {
            "ApplicationId": self.pinpoint_app_id,
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
        self.client.send_messages(MessageRequest=send_message_input)
