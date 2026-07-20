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

def test_urls():
    token = login()
    if not token: return
    headers = {"Authorization": f"Bearer {token}"}
    urls = [
        "/learning/domains/",
        "/learning/shop/courses/",
        "/learning/subcourses/",
        "/learning/mcqs/",
        "/learning/flashcards/",
        "/learning/api/quiz/scores"
    ]
    for path in urls:
        url = "https://www.akuraedu.com/api" + path
        res = requests.get(url, headers=headers)
        print(f"GET {path} -> {res.status_code}")
        if res.status_code != 200:
            print("ERROR BODY:", res.text[:200])

if __name__ == "__main__":
    test_urls()
