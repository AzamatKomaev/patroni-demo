import json
import time
import requests

from faker import Faker


fake = Faker()

APP_URL = "http://localhost:8080"


def create_post(title, description, author_name):
    headers = {
        "Content-Type": "application/json"
    }
    request_body = {
        "title": title,
        "description": description,
        "author_name": author_name
    }

    response = requests.post(f"{APP_URL}/api/v1/posts", data=json.dumps(request_body), headers=headers)
    return response.json()



while True:
    title = fake.name()
    description = fake.text()
    author_name = f"{title} {fake.user_name()}"
    response = create_post(title, description, author_name)
    print(response)
    time.sleep(0.01)
    
    
