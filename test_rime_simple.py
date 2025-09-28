#!/usr/bin/env python3
"""
Simple RIME.ai test with short text
"""

import os
import requests

def test_rime():
    """Test RIME.ai with simple text"""

    # Check for API key
    api_key = os.getenv('RIME_API_KEY')
    if not api_key:
        print("Error: RIME_API_KEY not found in environment")
        return False

    try:
        # Test with just one word
        text = "Hello, this is a test of Häagen-Dazs pronunciation."

        # Try alternative RIME.ai API endpoint
        url = "https://api.rime.ai/v1/rime-tts"

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "text": text,
            "speaker": "celeste",
            "modelId": "arcana",
            "audioFormat": "mp3"  # Try simpler format
        }

        print(f"Testing with: {text}")
        print("Sending request to RIME.ai...")
        response = requests.post(url, headers=headers, json=payload, timeout=60)

        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            with open("test_rime.mp3", 'wb') as f:
                f.write(response.content)
            print("✅ Test successful!")
            return True
        else:
            print(f"❌ Error: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_rime()