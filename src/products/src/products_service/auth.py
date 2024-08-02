from flask import Flask
from typing import Dict, Any
import boto3

cognito_idp = boto3.client('cognito-idp')

class Auth:

    def __init__(self, app: Flask | None = None):
        if app:
            self.init_app(app)

    def init_app(self, app: Flask):
        self.user_pool_id = app.config['COGNITO_USER_POOL_ID']

    def auth_user(self, cognito_authentication_provider: str) -> Dict[str, Any]:
        """
        cognito_authentication_provider: string with the following format: 
        cognito-idp.us-east-1.amazonaws.com/us-east-1_xxxxxxxx,cognito-idp.us-east-1.amazonaws.com/us-east-1_xxxxxxxxx:CognitoSignIn:xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
        The identity after the 'CognitoSignIn:' string represents the signed in user sub, which we use to lookup the user.
        """
        cognito_signin = [sign_in for sign_in in cognito_authentication_provider.split(',') if "CognitoSignIn" in sign_in]
        
        _, _, user_sub = cognito_signin[0].split(":")
        users = cognito_idp.list_users(UserPoolId=self.user_pool_id, Filter=f"sub = \"{user_sub}\"")
        user_attributes = users['Users'][0]['Attributes']
        data = {attribute['Name']: attribute['Value'] for attribute in user_attributes}
        
        return {
            "user_id": data['custom:profile_user_id'],
            "persona": data['custom:profile_persona'],
            "age": int(data['custom:profile_age'])            
        }