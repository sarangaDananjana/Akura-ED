import requests

def login():
    login_url = "https://www.akuraedu.com/api/users/auth/login/"
    payload = {
        "username": "sarangad",
        "password": "Iwantm0ney$"
    }
    res = requests.post(login_url, data=payload)
    if res.status_code == 200:
        return res.json().get("access")
    return None

def test_sync():
    token = login()
    if not token: return
    
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "reviews": [
            {
                "flashcardId": "2008",
                "status": "easy",
                "timestamp": "2026-07-21T00:00:00Z"
            }
        ]
    }
    res = requests.post("https://www.akuraedu.com/api/learning/api/flashcards/sync", json=payload, headers=headers)
    print("POST Status:", res.status_code)
    try:
        print("POST Body:", res.json())
    except:
        print("POST Body:", res.text[:500])

if __name__ == "__main__":
    test_sync()
