import requests

LIVEKIT_SERVER_URL = "http://your-livekit-server-url"
API_KEY = "your-api-key"
SECRET_KEY = "your-secret-key"

def create_room(room_name):
    token = generate_livekit_token(API_KEY, SECRET_KEY, "server", room_name)
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{LIVEKIT_SERVER_URL}/rooms", json={"name": room_name}, headers=headers)
    return response.json()

room_info = create_room("test-room")
print(room_info)
