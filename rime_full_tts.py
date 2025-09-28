#!/usr/bin/env python3
"""
RIME.ai TTS script for ALL challenging commercial words
Processes in batches due to 500 char limit, then concatenates
"""

import os
import sys
import requests
import json
import base64
from pydub import AudioSegment
import tempfile

def load_test_words(filename):
    """Load test words from file"""
    with open(filename, 'r', encoding='utf-8') as f:
        words = [line.strip() for line in f if line.strip()]
    return words

def create_batches(words, max_chars=400):
    """Split words into batches under character limit"""
    batches = []
    current_batch = []
    current_length = 0

    for word in words:
        # Calculate length if we add this word
        word_length = len(word) + 2  # +2 for ", "

        if current_length + word_length > max_chars and current_batch:
            # Start new batch
            batches.append(current_batch)
            current_batch = [word]
            current_length = len(word)
        else:
            current_batch.append(word)
            current_length += word_length

    if current_batch:
        batches.append(current_batch)

    return batches

def generate_rime_batch(words_batch, api_key):
    """Generate audio for a batch of words"""

    # Create text from batch
    text = ", ".join(words_batch) + "."

    # RIME.ai API endpoint
    url = "https://users.rime.ai/v1/rime-tts"

    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "speaker": "abbie",    # American female voice
        "text": text,
        "lang": "eng",         # English language
        "audioFormat": "mp3",  # Audio format
        "modelId": "mistv2"    # Use latest mistv2 model (Feb 2025)
    }

    print(f"Generating batch: {len(words_batch)} words, {len(text)} chars")
    response = requests.post(url, headers=headers, json=payload, timeout=60)

    if response.status_code == 200:
        response_data = response.json()
        if 'audioContent' in response_data:
            # Decode base64 audio content
            audio_bytes = base64.b64decode(response_data['audioContent'])
            return audio_bytes
        else:
            print(f"❌ No audioContent in response: {response_data}")
            return None
    else:
        print(f"❌ RIME.ai API error: {response.status_code}")
        print(f"Response: {response.text}")
        return None

def concatenate_audio_files(audio_segments, output_file):
    """Concatenate multiple audio segments with brief pauses"""

    combined = AudioSegment.empty()
    pause = AudioSegment.silent(duration=500)  # 500ms pause between batches

    for i, audio_bytes in enumerate(audio_segments):
        # Save to temporary file
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
            temp_file.write(audio_bytes)
            temp_path = temp_file.name

        # Load audio segment
        try:
            segment = AudioSegment.from_mp3(temp_path)
            combined += segment

            # Add pause between segments (except for the last one)
            if i < len(audio_segments) - 1:
                combined += pause

        except Exception as e:
            print(f"❌ Error processing segment {i}: {e}")
        finally:
            # Clean up temp file
            os.unlink(temp_path)

    # Export final combined audio
    combined.export(output_file, format="mp3")

def main():
    # Check for API key
    api_key = os.getenv('RIME_API_KEY')
    if not api_key:
        print("Error: RIME_API_KEY not found in environment")
        return False

    # Change to script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

    # Load test words
    words = load_test_words("test_words.txt")
    print(f"Loaded {len(words)} test words")

    # Create batches
    batches = create_batches(words, max_chars=400)
    print(f"Split into {len(batches)} batches")

    # Generate audio for each batch
    audio_segments = []
    for i, batch in enumerate(batches, 1):
        print(f"\nProcessing batch {i}/{len(batches)}...")
        audio_bytes = generate_rime_batch(batch, api_key)
        if audio_bytes:
            audio_segments.append(audio_bytes)
            print(f"✅ Batch {i} completed")
        else:
            print(f"❌ Batch {i} failed")
            return False

    # Concatenate all segments
    output_file = "rime_all_words_full.mp3"
    print(f"\nCombining {len(audio_segments)} audio segments...")

    try:
        concatenate_audio_files(audio_segments, output_file)
        print(f"✅ RIME.ai full audio saved to: {output_file}")

        # Show file size
        if os.path.exists(output_file):
            size = os.path.getsize(output_file) / 1024 / 1024  # MB
            print(f"📁 File size: {size:.2f} MB")
            print(f"📝 Total words: {len(words)}")

        return True

    except Exception as e:
        print(f"❌ Error combining audio: {e}")
        return False

if __name__ == "__main__":
    main()