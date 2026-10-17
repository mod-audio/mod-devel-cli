import base64
import json


class TokenHelper:
    USER_ID = 'dev@partner.com'

    @staticmethod
    def generate_token(user_id=USER_ID, **payload):
        # Unsigned: the CLI only decodes the payload, it never verifies the signature
        def encode(data: dict) -> str:
            return base64.urlsafe_b64encode(json.dumps(data).encode()).decode().rstrip('=')
        header = encode({'alg': 'EdDSA', 'typ': 'JWT'})
        return f'{header}.{encode({"sub": user_id, **payload})}.signature'
