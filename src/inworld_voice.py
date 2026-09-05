"""
FasalRakshak - Sarvam AI High-Fidelity Regional Voice Synthesis Engine
Provides human-fidelity, natural regional voice narration for crop disease remedies
supporting 10 Indian regional languages and English via Sarvam AI bulbul TTS models.
"""

import os
import hashlib
import json
import base64
from pathlib import Path
import requests
from io import BytesIO
from typing import Dict, Any, Optional
import sys
from dotenv import load_dotenv

load_dotenv()

sys.path.append(str(Path(__file__).resolve().parent.parent))
import config

SARVAM_API_KEY = os.getenv("SARVAM_API_KEY", "")
SARVAM_TTS_ENDPOINT = "https://api.sarvam.ai/text-to-speech"

# Language code mapping for Sarvam AI bulbul TTS
SARVAM_LANG_MAP = {
    "hindi": "hi-IN",
    "khortha": "hi-IN",
    "nagpuri": "hi-IN",
    "bhojpuri": "hi-IN",
    "english": "en-IN",
    "bengali": "bn-IN",
    "tamil": "ta-IN",
    "telugu": "te-IN",
    "marathi": "mr-IN",
    "gujarati": "gu-IN",
    "punjabi": "pa-IN",
}

# gTTS fallback language mapping
GTTS_LANG_MAP = {
    "hindi": "hi",
    "khortha": "hi",
    "nagpuri": "hi",
    "bhojpuri": "hi",
    "english": "en",
    "bengali": "bn",
    "tamil": "ta",
    "telugu": "te",
    "marathi": "mr",
    "gujarati": "gu",
    "punjabi": "pa",
}


class InworldVoiceEngine:
    """
    High-Fidelity AI Voice Engine powered by Sarvam AI Neural Speech Synthesis
    with automatic local caching and gTTS neural fallback.
    """

    def __init__(self):
        self.cache_dir = config.ASSETS_DIR / "inworld_audio"
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def synthesize_speech(self, text: str, language: str = "Hindi") -> Dict[str, Any]:
        """
        Synthesizes human-realistic voice audio using Sarvam AI TTS in the chosen language.
        Returns dictionary with audio_file path, audio source, and metadata.
        """
        if not text or not text.strip():
            text = "फसल स्वास्थ्य सलाह उपलब्ध है।"

        clean_text = text.replace("*", "").replace("#", "").strip()
        lang_key = language.lower()
        text_hash = hashlib.md5(f"{clean_text}_{lang_key}".encode("utf-8")).hexdigest()

        # 1. Check local Sarvam audio cache
        sarvam_cache_file = self.cache_dir / f"sarvam_{text_hash}.wav"
        if sarvam_cache_file.exists() and sarvam_cache_file.stat().st_size > 1000:
            return {
                "source": "Sarvam AI Neural Voice (Cached)",
                "audio_file": str(sarvam_cache_file),
                "has_audio": True,
                "text": clean_text
            }

        # 2. Attempt Sarvam AI Text-to-Speech synthesis
        api_key = os.getenv("SARVAM_API_KEY") or SARVAM_API_KEY
        if api_key:
            target_lang_code = SARVAM_LANG_MAP.get(lang_key, "hi-IN")
            try:
                headers = {
                    "api-subscription-key": api_key,
                    "Content-Type": "application/json"
                }
                payload = {
                    "inputs": [clean_text[:500]],
                    "target_language_code": target_lang_code,
                    "speaker": "shubh",
                    "model": "bulbul:v3",
                    "pace": 1.0
                }
                resp = requests.post(
                    SARVAM_TTS_ENDPOINT,
                    headers=headers,
                    json=payload,
                    timeout=12
                )
                if resp.status_code == 200:
                    resp_data = resp.json()
                    audios = resp_data.get("audios", [])
                    if audios and len(audios[0]) > 0:
                        audio_bytes = base64.b64decode(audios[0])
                        with open(sarvam_cache_file, "wb") as f:
                            f.write(audio_bytes)
                        return {
                            "source": "Sarvam AI Neural Voice",
                            "audio_file": str(sarvam_cache_file),
                            "has_audio": True,
                            "text": clean_text
                        }
                    else:
                        print(f"[Sarvam Voice Note] No audio data in response: {resp_data}")
                else:
                    print(f"[Sarvam Voice Warning] HTTP {resp.status_code}: {resp.text[:200]}")
            except Exception as e:
                print(f"[Sarvam Voice Warning] API call failed: {e}. Falling back to gTTS.")

        # 3. Check gTTS fallback cache
        gtts_cache_file = self.cache_dir / f"gtts_{text_hash}.mp3"
        if gtts_cache_file.exists() and gtts_cache_file.stat().st_size > 1000:
            return {
                "source": "gTTS Fallback (Cached)",
                "audio_file": str(gtts_cache_file),
                "has_audio": True,
                "text": clean_text
            }

        # 4. Fallback to gTTS
        try:
            from gtts import gTTS
            gtts_code = GTTS_LANG_MAP.get(lang_key, "hi")
            tts = gTTS(text=clean_text, lang=gtts_code, slow=False)
            tts.save(str(gtts_cache_file))
            return {
                "source": "gTTS Fallback Voice",
                "audio_file": str(gtts_cache_file),
                "has_audio": True,
                "text": clean_text
            }
        except Exception as e:
            print(f"[Voice Synthesis Error]: {e}")
            return {
                "source": "error",
                "audio_file": None,
                "has_audio": False,
                "text": clean_text
            }


if __name__ == "__main__":
    engine = InworldVoiceEngine()
    res = engine.synthesize_speech("आलू की फसल में पछेता झुलसा रोग है। नीम के तेल का छिड़काव करें।", "Hindi")
    print("[Sarvam Voice Engine Test]:", res)
