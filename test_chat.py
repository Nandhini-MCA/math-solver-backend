import requests

def test_chat():
    # Login
    login_url = "http://localhost:8000/auth/login"
    login_data = {"email": "test3@example.com", "password": "password123"}
    login_res = requests.post(login_url, json=login_data)
    if login_res.status_code != 200:
        print(f"Login failed: {login_res.text}")
        return
        
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Chat
    chat_url = "http://localhost:8000/chat/"
    chat_data = {"message": "Hello, can you help me with Newton's second law?"}
    chat_res = requests.post(chat_url, json=chat_data, headers=headers)
    
    print(f"Chat status: {chat_res.status_code}")
    print(f"Chat response: {chat_res.text}")

if __name__ == "__main__":
    test_chat()
