#!/usr/bin/env python3
"""
Generate natural sentences using challenging commercial brand names
Tests TTS pronunciation in conversational context
"""

import os
import sys
import requests
import json
import base64

def get_test_sentences():
    """Return natural sentences organized by category"""
    sentences = [
        # Food & Beverage
        "I love starting my morning with Häagen-Dazs ice cream, some fresh açaí bowls, and a quick stop at Chipotle for lunch.",

        "My grocery list includes Nutella for breakfast, La Croix sparkling water, and some Ghirardelli chocolate for dessert.",

        "The restaurant served bruschetta with sriracha sauce, and I ordered Worcestershire dressing on my quinoa salad.",

        # Technology
        "My new Huawei phone works great with my ASUS laptop, though I'm thinking of switching to Xiaomi next year.",

        "I prefer using PostgreSQL databases over MySQL when building applications, especially with Kubernetes deployment.",

        "The Bose headphones sound amazing, but Adobe software keeps crashing on my computer.",

        # Fashion & Luxury
        "She wore a beautiful Hermès scarf with her Givenchy dress to the Versace fashion show.",

        "The boutique featured Yves Saint Laurent handbags, Balenciaga sneakers, and elegant Moschino accessories.",

        "I found a vintage Loewe bag and some Bvlgari jewelry at the luxury consignment store.",

        # Automotive
        "His dream garage includes a Porsche sports car, a classic Peugeot sedan, and a reliable Hyundai SUV.",

        "The Volkswagen dealership is next to the Citroën showroom, but I'm really interested in that Koenigsegg supercar.",

        # Pharmaceuticals & Healthcare
        "The doctor prescribed Tylenol for pain relief and mentioned that Pfizer makes excellent vaccines.",

        "My prescription includes Xeljanz for arthritis, Humira injections, and Ozempic for diabetes management.",

        # Retail & Lifestyle
        "We shopped at IKEA for furniture, then stopped by the Swedish brand Fjällräven for hiking gear.",

        "The Czech car manufacturer Škoda has great reviews, and I enjoyed a Hoegaarden beer while researching cars.",

        "I'm saving up for a Tag Heuer watch and maybe an Audemars Piguet timepiece for special occasions.",

        # Modern Tech & Social
        "My Oculus headset works perfectly for virtual meetings, and I post about it constantly on TikTok.",

        "I use Lyft to get around the city, especially when I'm running late for important meetings."
    ]

    return sentences

def generate_elevenlabs_audio(text, output_file, api_key):
    """Generate audio using ElevenLabs API"""

    voice_id = "21m00Tcm4TlvDq8ikWAM"  # Rachel
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": api_key
    }

    data = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "language_code": "en",
        "voice_settings": {
            "stability": 0.75,
            "similarity_boost": 0.75,
            "style": 0.0,
            "use_speaker_boost": True
        }
    }

    print("Generating ElevenLabs audio...")
    response = requests.post(url, json=data, headers=headers, timeout=120)

    if response.status_code == 200:
        with open(output_file, 'wb') as f:
            f.write(response.content)
        return True
    else:
        print(f"❌ ElevenLabs error: {response.status_code} - {response.text}")
        return False

def generate_rime_sentences(sentences, api_key):
    """Generate audio for sentences using RIME.ai API with batching"""

    # RIME has 500 char limit, so we'll process sentences individually
    sentence_files = []

    url = "https://users.rime.ai/v1/rime-tts"
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    for i, sentence in enumerate(sentences, 1):
        if len(sentence) > 500:
            print(f"⚠️ Sentence {i} too long ({len(sentence)} chars), skipping")
            continue

        payload = {
            "speaker": "abbie",
            "text": sentence,
            "lang": "eng",
            "audioFormat": "mp3",
            "modelId": "mistv2"    # Use latest mistv2 model (Feb 2025)
        }

        print(f"Generating sentence {i}/{len(sentences)} ({len(sentence)} chars)")
        response = requests.post(url, headers=headers, json=payload, timeout=60)

        if response.status_code == 200:
            response_data = response.json()
            if 'audioContent' in response_data:
                audio_bytes = base64.b64decode(response_data['audioContent'])

                sentence_file = f"rime_sentence_{i:02d}.mp3"
                with open(sentence_file, 'wb') as f:
                    f.write(audio_bytes)

                sentence_files.append(sentence_file)
                print(f"✅ Saved {sentence_file}")
            else:
                print(f"❌ No audioContent in sentence {i}")
        else:
            print(f"❌ RIME error for sentence {i}: {response.status_code}")

    return sentence_files

def concatenate_rime_files(sentence_files, output_file):
    """Concatenate RIME sentence files using ffmpeg"""

    if not sentence_files:
        print("❌ No sentence files to concatenate")
        return False

    # Create file list for ffmpeg
    with open('sentence_list.txt', 'w') as f:
        for sentence_file in sentence_files:
            f.write(f"file '{sentence_file}'\n")

    try:
        import subprocess
        cmd = ['ffmpeg', '-f', 'concat', '-safe', '0', '-i', 'sentence_list.txt', '-c', 'copy', output_file, '-y']
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            print(f"✅ RIME sentences concatenated to {output_file}")

            # Clean up
            for sentence_file in sentence_files:
                os.remove(sentence_file)
            os.remove('sentence_list.txt')

            return True
        else:
            print(f"❌ ffmpeg error: {result.stderr}")
            return False

    except Exception as e:
        print(f"❌ Concatenation error: {e}")
        return False

def main():
    # Check API keys
    elevenlabs_key = os.getenv('ELEVENLABS_API_KEY')
    rime_key = os.getenv('RIME_API_KEY')

    if not elevenlabs_key:
        print("❌ ELEVENLABS_API_KEY not found")
        return
    if not rime_key:
        print("❌ RIME_API_KEY not found")
        return

    # Change to script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

    # Get test sentences
    sentences = get_test_sentences()
    print(f"Generated {len(sentences)} test sentences")

    # Show the sentences
    print("\n📝 TEST SENTENCES:")
    print("=" * 60)
    for i, sentence in enumerate(sentences, 1):
        category = ""
        if i <= 3:
            category = "🍔 Food & Beverage"
        elif i <= 6:
            category = "💻 Technology"
        elif i <= 9:
            category = "👗 Fashion & Luxury"
        elif i <= 11:
            category = "🚗 Automotive"
        elif i <= 13:
            category = "💊 Pharmaceuticals"
        elif i <= 16:
            category = "🏪 Retail & Lifestyle"
        else:
            category = "📱 Modern Tech"

        print(f"\n{category} - Sentence {i}:")
        print(f"{sentence}")
        print(f"({len(sentence)} characters)")

    print("\n" + "=" * 60)

    # Create combined text for ElevenLabs (no char limit)
    combined_text = " ".join(sentences)
    print(f"\nCombined text length: {len(combined_text)} characters")

    # Generate ElevenLabs audio
    print(f"\n🎵 Generating ElevenLabs audio...")
    elevenlabs_file = "elevenlabs_sentences.mp3"
    if generate_elevenlabs_audio(combined_text, elevenlabs_file, elevenlabs_key):
        size = os.path.getsize(elevenlabs_file) / 1024 / 1024
        print(f"✅ ElevenLabs: {elevenlabs_file} ({size:.2f} MB)")

    # Generate RIME audio (sentence by sentence due to 500 char limit)
    print(f"\n🎵 Generating RIME.ai audio...")
    sentence_files = generate_rime_sentences(sentences, rime_key)

    if sentence_files:
        rime_file = "rime_sentences.mp3"
        if concatenate_rime_files(sentence_files, rime_file):
            size = os.path.getsize(rime_file) / 1024 / 1024
            print(f"✅ RIME.ai: {rime_file} ({size:.2f} MB)")

    print(f"\n🎧 Both audio files ready for comparison!")
    print("Open both files in QuickTime Player to compare pronunciation quality.")

if __name__ == "__main__":
    main()