#!/usr/bin/env python3
"""
RIME.ai TTS script for ALL challenging commercial words
Simple approach: process in batches, save separate files, then use ffmpeg to concatenate
"""

import os
import sys
import requests
import json
import base64
import subprocess

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

def generate_rime_batch(words_batch, api_key, batch_num):
    """Generate audio for a batch of words"""

    # Create text from batch
    text = ", ".join(words_batch) + "."
    output_file = f"rime_batch_{batch_num:02d}.mp3"

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

    print(f"Batch {batch_num}: {len(words_batch)} words, {len(text)} chars")
    response = requests.post(url, headers=headers, json=payload, timeout=60)

    if response.status_code == 200:
        response_data = response.json()
        if 'audioContent' in response_data:
            # Decode base64 audio content
            audio_bytes = base64.b64decode(response_data['audioContent'])

            # Save to file
            with open(output_file, 'wb') as f:
                f.write(audio_bytes)

            print(f"✅ Saved {output_file}")
            return output_file
        else:
            print(f"❌ No audioContent in response: {response_data}")
            return None
    else:
        print(f"❌ RIME.ai API error: {response.status_code}")
        print(f"Response: {response.text}")
        return None

def concatenate_with_ffmpeg(batch_files, output_file):
    """Use ffmpeg to concatenate MP3 files"""

    # Create a file list for ffmpeg
    with open('file_list.txt', 'w') as f:
        for batch_file in batch_files:
            f.write(f"file '{batch_file}'\n")

    # Use ffmpeg to concatenate
    try:
        cmd = ['ffmpeg', '-f', 'concat', '-safe', '0', '-i', 'file_list.txt', '-c', 'copy', output_file, '-y']
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            print(f"✅ Successfully concatenated to {output_file}")

            # Clean up batch files and file list
            for batch_file in batch_files:
                os.remove(batch_file)
            os.remove('file_list.txt')

            return True
        else:
            print(f"❌ ffmpeg error: {result.stderr}")
            return False

    except FileNotFoundError:
        print("❌ ffmpeg not found. Installing via homebrew...")
        try:
            subprocess.run(['brew', 'install', 'ffmpeg'], check=True)
            print("✅ ffmpeg installed. Retrying concatenation...")
            return concatenate_with_ffmpeg(batch_files, output_file)
        except subprocess.CalledProcessError:
            print("❌ Failed to install ffmpeg")
            return False

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
    batch_files = []
    for i, batch in enumerate(batches, 1):
        print(f"\nProcessing batch {i}/{len(batches)}...")
        batch_file = generate_rime_batch(batch, api_key, i)
        if batch_file:
            batch_files.append(batch_file)
        else:
            print(f"❌ Batch {i} failed")
            return False

    # Concatenate all files
    output_file = "rime_all_words_full.mp3"
    print(f"\nCombining {len(batch_files)} audio files...")

    if concatenate_with_ffmpeg(batch_files, output_file):
        # Show file size
        if os.path.exists(output_file):
            size = os.path.getsize(output_file) / 1024 / 1024  # MB
            print(f"📁 File size: {size:.2f} MB")
            print(f"📝 Total words: {len(words)}")

        return True
    else:
        return False

if __name__ == "__main__":
    main()