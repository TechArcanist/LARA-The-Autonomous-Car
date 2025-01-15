import jwt
import time

def generate_livekit_token(api_key, secret_key, identity, room):
    """
    Generate a LiveKit token for authentication.
    """
    payload = {
        "video": {"room": room, "participant": identity},
        "iss": api_key,
        "exp": int(time.time()) + 3600  # Token valid for 1 hour
    }
    token = jwt.encode(payload, secret_key, algorithm="HS256")
    return token
