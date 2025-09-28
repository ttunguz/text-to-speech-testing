#!/usr/bin/env python3
"""
RIME.ai TTS script for testing challenging commercial words
Generates a single combined audio file with all test words
"""

import os
import sys
import requests
import time
import json

def load_test_words(filename):
    """Load test words from file"""
    with open(filename, 'r', encoding='utf-8') as f:
        words = [line.strip() for line in f if line.strip()]
    return words

def create_combined_text(words):
    """Create text with proper spacing for TTS - limit to 500 chars for RIME"""
    # For RIME: shorter format to fit 500 char limit
    # Just the words with commas, no numbers
    text = ", ".join(words[:25])  # Take first 25 words to stay under 500 chars
    return text + "."

def generate_rime_audio(text, output_file):
    """Generate audio using RIME.ai API"""

    # Check for API key
    api_key = os.getenv('RIME_API_KEY')
    if not api_key:
        print("Error: RIME_API_KEY not found in environment")
        return False

    try:
        print("Generating RIME.ai audio...")
        print(f"Text length: {len(text)} characters")

        # RIME.ai API endpoint
        url = "https://users.rime.ai/v1/rime-tts"

        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        # Use Abbie voice (available in default mist model)
        payload = {
            "speaker": "abbie",    # American female voice
            "text": text,
            "lang": "eng",         # English language
            "audioFormat": "mp3",  # Audio format
            "modelId": "mistv2"    # Use latest mistv2 model (Feb 2025)
        }

        print("Sending request to RIME.ai...")
        response = requests.post(url, headers=headers, json=payload, timeout=120)

        if response.status_code == 200:
            # RIME returns JSON with base64-encoded audio
            import json
            import base64

            response_data = response.json()
            if 'audioContent' in response_data:
                # Decode base64 audio content
                audio_bytes = base64.b64decode(response_data['audioContent'])
                with open(output_file, 'wb') as f:
                    f.write(audio_bytes)
                print(f"✅ RIME.ai audio saved to: {output_file}")
                return True
            else:
                print(f"❌ No audioContent in response: {response_data}")
                return False
        else:
            print(f"❌ RIME.ai API error: {response.status_code}")
            print(f"Response: {response.text}")
            return False

    except requests.exceptions.Timeout:
        print("❌ Request timed out - try reducing text length")
        return False
    except Exception as e:
        print(f"❌ Error generating RIME.ai audio: {e}")
        return False

def main():
    # Change to script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

    # Load test words
    words = load_test_words("test_words.txt")
    print(f"Loaded {len(words)} test words")

    # Create combined text
    combined_text = create_combined_text(words)

    # Generate audio
    output_file = "rime_all_words.mp3"
    success = generate_rime_audio(combined_text, output_file)

    if success:
        print(f"\n🎉 Successfully generated {output_file}")
        print(f"📝 Words included: {len(words)}")

        # Show file size
        if os.path.exists(output_file):
            size = os.path.getsize(output_file) / 1024 / 1024  # MB
            print(f"📁 File size: {size:.2f} MB")
    else:
        print("\n❌ Failed to generate audio")
        sys.exit(1)

if __name__ == "__main__":
    main()