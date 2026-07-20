import requests

# 1. Login to get the access token
login_url = "https://www.akuraedu.com/api/users/auth/login/"
print(f"Logging in to {login_url}...")

login_payload = {
    "username": "sarangad",
    "password": "Iwantm0ney$"
}

response = requests.post(login_url, json=login_payload)
print("Login Response Code:", response.status_code)

if response.status_code != 200:
    print("Login Failed:", response.text)
    exit(1)

token = response.json().get('access')
print("Login successful! Got access token.")

# 2. Trigger the sync API
# Note: Based on your urls.py, the path is api/learning/ -> api/flashcards/sync
sync_url = "https://www.akuraedu.com/api/learning/api/flashcards/sync"
print(f"\nTriggering sync at {sync_url}...")

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

sync_payload = {
    "reviews": [
        {
            "flashcardId": "dummy_card_999",
            "status": "known"
        },
        {
            "flashcardId": "dummy_card_888",
            "status": "learning"
        }
    ]
}

sync_response = requests.post(sync_url, json=sync_payload, headers=headers)
print("Sync Response Code:", sync_response.status_code)
print("Sync Response Body:", sync_response.text)

print("\nDone! If you got a 200 OK, the data is now in MongoDB. Go refresh Compass!")
