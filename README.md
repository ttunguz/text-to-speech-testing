# Text-to-Speech API Comparison: ElevenLabs vs RIME.ai

A comprehensive comparison of text-to-speech pronunciation quality between ElevenLabs & RIME.ai APIs, specifically testing challenging commercial brand names & trademarks.

## Overview

This project tests the claim that RIME.ai provides superior pronunciation of difficult commercial terms compared to ElevenLabs. We evaluate both APIs using:

1. **46 challenging commercial words** across 5 categories
2. **18 natural conversational sentences** incorporating these brand names

## Quick Start

**Immediate Testing (No API Keys Required):**
1. Clone this repository
2. Open the included MP3 files in any audio player
3. Compare pronunciation quality between ElevenLabs and RIME mistv2

**Generate New Audio:**
1. Set API keys in environment variables
2. Run the Python scripts to generate fresh audio files
3. Compare results with included samples

## Test Categories

- **Food & Beverage**: Haagen-Dazs, Acai, Chipotle, Nutella, La Croix, Ghirardelli, Worcestershire, Sriracha, Quinoa
- **Technology**: Huawei, ASUS, Xiaomi, PostgreSQL, MySQL, Kubernetes, Bose, Adobe
- **Fashion & Luxury**: Hermes, Givenchy, Versace, Yves Saint Laurent, Balenciaga, Moschino, Loewe, Bvlgari
- **Automotive**: Porsche, Peugeot, Hyundai, Volkswagen, Citroen, Koenigsegg
- **Pharmaceuticals**: Tylenol, Pfizer, Xeljanz, Humira, Ozempic
- **Retail & Lifestyle**: IKEA, Fjallraven, Skoda, Hoegaarden, Audemars Piguet, Oculus, TikTok, Lyft

## Scripts

### Word List Testing

- **`elevenlabs_tts.py`**: Generates audio for all 46 words using ElevenLabs API
  - Voice: Rachel (American female)
  - Model: eleven_multilingual_v2
  - Single API call for all words

- **`rime_tts.py`**: Basic RIME.ai implementation (limited to 25 words due to 500-char API limit)
  - Voice: Abbie (American female)
  - Model: mistv2 (February 2025 - enhanced pronunciation)

- **`rime_full.py`**: Complete RIME.ai implementation with batching
  - Processes all 46 words in batches under 400 characters
  - Uses ffmpeg for audio concatenation
  - Handles RIME's 500-character API limit
  - Model: mistv2 (February 2025 - enhanced pronunciation)

### Conversational Testing

- **`sentence_test_script.py`**: Generates natural sentences using brand names
  - 18 conversational sentences across all categories
  - Tests pronunciation in realistic contexts
  - Compares both APIs with identical content

## Setup

### Prerequisites

```bash
# Install dependencies
brew install ffmpeg  # For audio concatenation
pip install requests  # For API calls
```

### API Keys

Set environment variables in `~/.zshrc`:

```bash
export ELEVENLABS_API_KEY="your_elevenlabs_key"
export RIME_API_KEY="your_rime_key"
```

### Usage

```bash
# Test individual words
python elevenlabs_tts.py          # Generates: elevenlabs_all_words.mp3
python rime_full.py               # Generates: rime_all_words_full.mp3

# Test conversational sentences
python sentence_test_script.py    # Generates: elevenlabs_sentences.mp3 & rime_sentences.mp3
```

## Technical Details

### ElevenLabs API
- **Endpoint**: `https://api.elevenlabs.io/v1/text-to-speech/{voice_id}`
- **Response**: Direct MP3 binary data
- **Character Limit**: No practical limit for this use case
- **Language**: Explicitly set to English (`"language_code": "en"`)

### RIME.ai API
- **Endpoint**: `https://users.rime.ai/v1/rime-tts`
- **Response**: JSON with base64-encoded audio content
- **Character Limit**: 500 characters (requires batching)
- **Language**: Set to English (`"lang": "eng"`)

### Key Implementation Differences

1. **Response Format**: ElevenLabs returns raw MP3 bytes, RIME returns JSON with base64 audio
2. **Batching**: RIME requires splitting long text into <500 character chunks
3. **Concatenation**: RIME batches need ffmpeg to combine into single file

## Results

Audio files are generated for direct A/B comparison:

- `elevenlabs_all_words.mp3` - All 46 words via ElevenLabs
- `rime_all_words_full.mp3` - All 46 words via RIME.ai (batched)
- `elevenlabs_sentences.mp3` - 18 conversational sentences via ElevenLabs
- `rime_sentences.mp3` - 18 conversational sentences via RIME.ai

Open in QuickTime Player or any audio player to compare pronunciation quality.

## File Structure

```
text_to_speech_testing/
├── README.md
├── comparison_report.txt          # Detailed test configuration & methodology
├── test_words.txt                 # Master list of 46 challenging words
├── pyproject.toml                 # Python project configuration
├── .gitignore                     # Excludes API keys & temp files
│
├── Scripts/
│   ├── elevenlabs_tts.py          # ElevenLabs word testing
│   ├── rime_tts.py                # Basic RIME implementation (25 words)
│   ├── rime_full.py               # Complete RIME with batching (46 words)
│   └── sentence_test_script.py    # Conversational sentence testing
│
└── Audio Samples/
    ├── elevenlabs_all_words.mp3   # ElevenLabs: 46 words (634 KB)
    ├── elevenlabs_sentences.mp3   # ElevenLabs: 18 sentences (1.8 MB)
    ├── rime_all_words_full.mp3    # RIME mistv2: 46 words (174 KB)
    └── rime_sentences.mp3         # RIME mistv2: 18 sentences (583 KB)
```

## Notes

- **Sample audio files included** for immediate testing without API keys
- **API keys never committed** to version control (.gitignore protection)
- **RIME.ai batching** handles 500-character API limit automatically
- **Voice consistency** - Both APIs use American female voices for fair comparison
- **mistv2 model** provides enhanced pronunciation for challenging commercial terms