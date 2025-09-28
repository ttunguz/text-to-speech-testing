#!/usr/bin/env python3
"""
List available RIME.ai voices
"""

import os
import requests

def list_rime_voices():
    """List available RIME.ai voices"""

    # Check for API key
    api_key = os.getenv('RIME_API_KEY')
    if not api_key:
        print("Error: RIME_API_KEY not found in environment")
        return

    try:
        # RIME.ai voices endpoint
        url = "https://users.rime.ai/v1/rime-voices"

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        print("Fetching RIME.ai voices...")
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            voices = response.json()
            print("Available RIME.ai voices:")
            print("=" * 50)

            for voice in voices:
                print(f"Name: {voice.get('name', 'N/A')}")
                print(f"Language: {voice.get('language', 'N/A')}")
                print(f"Gender: {voice.get('gender', 'N/A')}")
                print(f"Description: {voice.get('description', 'N/A')}")
                print("-" * 30)

        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    list_rime_voices()