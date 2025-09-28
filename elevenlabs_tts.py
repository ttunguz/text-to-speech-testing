#!/usr/bin/env python3
"""
ElevenLabs TTS script for testing challenging commercial words
Generates a single combined audio file with all test words
"""

import os
import sys
import requests
import time

def load_test_words(filename):
    """Load test words from file"""
    with open(filename, 'r', encoding='utf-8') as f:
        words = [line.strip() for line in f if line.strip()]
    return words

def create_combined_text(words):
    """Create text with proper spacing for TTS - no numbers"""
    # Just the words with commas, no numbers (to match RIME format)
    text = ", ".join(words)
    return text + "."

def generate_elevenlabs_audio(text, output_file):
    """Generate audio using ElevenLabs API"""

    # Check for API key
    api_key = os.getenv('ELEVENLABS_API_KEY')
    if not api_key:
        print("Error: ELEVENLABS_API_KEY not found in environment")
        return False

    try:
        print("Generating ElevenLabs audio...")
        print(f"Text length: {len(text)} characters")

        # Use Rachel voice (American female) - clear American accent
        voice_id = "21m00Tcm4TlvDq8ikWAM"  # Rachel

        # ElevenLabs API endpoint
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": api_key
        }

        data = {
            "text": text,
            "model_id": "eleven_multilingual_v2",
            "language_code": "en",  # Explicitly specify English
            "voice_settings": {
                "stability": 0.75,
                "similarity_boost": 0.75,
                "style": 0.0,
                "use_speaker_boost": True
            }
        }

        print("Sending request to ElevenLabs...")
        response = requests.post(url, json=data, headers=headers, timeout=120)

        if response.status_code == 200:
            with open(output_file, 'wb') as f:
                f.write(response.content)
            print(f"✅ ElevenLabs audio saved to: {output_file}")
            return True
        else:
            print(f"❌ ElevenLabs API error: {response.status_code}")
            print(f"Response: {response.text}")
            return False

    except requests.exceptions.Timeout:
        print("❌ Request timed out - try reducing text length")
        return False
    except Exception as e:
        print(f"❌ Error generating ElevenLabs audio: {e}")
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
    output_file = "elevenlabs_all_words.mp3"
    success = generate_elevenlabs_audio(combined_text, output_file)

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