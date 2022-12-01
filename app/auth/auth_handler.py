from datetime import datetime, timedelta
from jose import jwt
from config import Config


conf = Config()

def token_response(token: str, exp: str):
    return {
        "access_token": token,
        "expires": exp.strftime("%Y-%m-%d %H:%M:%S")
    }


def signJWT(user_id: str) -> dict[str, str]:
    
    expires = datetime.now() + timedelta(days=5)
    payload = {
        "user_id": user_id,
        "expires": expires.strftime("%Y-%m-%d %H:%M:%S")
    }
    token = jwt.encode(
        payload, conf.JWT_SECRET, algorithm=conf.JWT_ALGO
        )
    return token_response(token, expires)


def decodeJWT(token: str) -> dict:
    try:
        decoded_token = jwt.decode(
            token, conf.JWT_SECRET, algorithms=[conf.JWT_ALGO]
            )
        token_expires = datetime.strptime(decoded_token["expires"], "%Y-%m-%d %H:%M:%S")
        if token_expires >= datetime.now():
            return decoded_token
        return None
    except:
        return {}
