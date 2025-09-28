#!/usr/bin/env python3
import os
import requests

api_key = os.getenv('RIME_API_KEY')

# Exact format from RIME docs
url = "https://users.rime.ai/v1/rime-tts"
headers = {
    'Accept': 'application/json',
    'Authorization': f'Bearer {api_key}',
    'Content-Type': 'application/json'
}

data = {
    "speaker": "abbie",
    "text": "Hello world",
    "lang": "eng",
    "audioFormat": "mp3"
}

print("Testing minimal RIME request...")
response = requests.post(url, headers=headers, json=data)
print(f"Status: {response.status_code}")
print(f"Response: {response.text[:200]}")

if response.status_code == 200:
    with open('rime_test.mp3', 'wb') as f:
        f.write(response.content)
    print("✅ Success!")