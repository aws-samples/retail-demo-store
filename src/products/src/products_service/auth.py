from flask import Flask, current_app
from typing import Dict, Any
import jwt
from jwt import PyJWKClient

class Auth:

    def __init__(self, app: Flask | None = None):
        if app:
            self.init_app(app)

    def init_app(self, app: Flask):
        region = app.config['AWS_DEFAULT_REGION']
        self.user_pool_id = app.config['USER_POOL_ID']
        self.verify = app.config.get('VERIFY_IDENTITY_TOKEN', True)
        self.audience = app.config['TOKEN_AUDIENCE']
        self.issuer = f"https://cognito-idp.{region}.amazonaws.com/{self.user_pool_id}"
        url = f"https://cognito-idp.{region}.amazonaws.com/{self.user_pool_id}/.well-known/jwks.json"
        self.jwks_client = PyJWKClient(url)

    def auth_user(self, id_token: str) -> Dict[str, Any]:
        try:
            signing_key = self.jwks_client.get_signing_key_from_jwt(id_token).key if self.verify else None
            data = jwt.decode(
                id_token,
                signing_key,
                algorithms=["RS256"],
                audience=self.audience,
                issuer=self.issuer,
                options={"verify_exp": self.verify, "verify_signature": self.verify}
            )            
        except Exception as e:
            current_app.logger.error("Error decoding JWT token", exc_info=e)
            return None
        else:
            current_app.logger.debug("Authenticated identity token")
            return {
                "user_id": data['custom:profile_user_id'],
                "persona": data['custom:profile_persona'],
                "age": int(data['custom:profile_age'])
            }
