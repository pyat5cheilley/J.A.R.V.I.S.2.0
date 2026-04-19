"""Voice input/output handler for J.A.R.V.I.S. 2.0

Handles text-to-speech and speech-to-text functionality.
Uses pyttsx3 for TTS and speech_recognition for STT.
"""

import os
import logging
import threading
import pyttsx3
import speech_recognition as sr
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

# Voice configuration from environment
VOICE_RATE = int(os.getenv("VOICE_RATE", 175))
VOICE_VOLUME = float(os.getenv("VOICE_VOLUME", 0.9))
VOICE_INDEX = int(os.getenv("VOICE_INDEX", 0))  # 0=default, 1=alternate
MIC_TIMEOUT = int(os.getenv("MIC_TIMEOUT", 5))
MIC_PHRASE_LIMIT = int(os.getenv("MIC_PHRASE_LIMIT", 10))

# Thread lock to prevent concurrent speech
_tts_lock = threading.Lock()
_engine = None


def _get_engine() -> pyttsx3.Engine:
    """Lazily initialize and return the TTS engine."""
    global _engine
    if _engine is None:
        _engine = pyttsx3.init()
        _engine.setProperty("rate", VOICE_RATE)
        _engine.setProperty("volume", VOICE_VOLUME)
        voices = _engine.getProperty("voices")
        if voices and VOICE_INDEX < len(voices):
            _engine.setProperty("voice", voices[VOICE_INDEX].id)
        logger.info("TTS engine initialized (rate=%d, volume=%.1f)", VOICE_RATE, VOICE_VOLUME)
    return _engine


def speak(text: str) -> bool:
    """Convert text to speech and play it.

    Args:
        text: The text to speak aloud.

    Returns:
        True on success, False if TTS fails.
    """
    if not text or not text.strip():
        return False

    with _tts_lock:
        try:
            engine = _get_engine()
            engine.say(text)
            engine.runAndWait()
            return True
        except Exception as e:
            logger.error("TTS error: %s", e)
            return False


def listen(prompt: str = "") -> str | None:
    """Listen for voice input via microphone and return transcribed text.

    Args:
        prompt: Optional text to speak before listening.

    Returns:
        Transcribed string, or None if recognition fails.
    """
    if prompt:
        speak(prompt)

    recognizer = sr.Recognizer()
    recognizer.pause_threshold = 0.8

    try:
        with sr.Microphone() as source:
            logger.info("Adjusting for ambient noise...")
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            logger.info("Listening...")
            audio = recognizer.listen(
                source,
                timeout=MIC_TIMEOUT,
                phrase_time_limit=MIC_PHRASE_LIMIT,
            )

        text = recognizer.recognize_google(audio)
        logger.info("Recognized: %s", text)
        return text.strip()

    except sr.WaitTimeoutError:
        logger.warning("Microphone timed out — no speech detected.")
        return None
    except sr.UnknownValueError:
        logger.warning("Speech not understood.")
        return None
    except sr.RequestError as e:
        logger.error("Speech recognition service error: %s", e)
        return None
    except Exception as e:
        logger.error("Unexpected listen error: %s", e)
        return None


def is_voice_available() -> bool:
    """Check whether a microphone is available on this system."""
    try:
        mics = sr.Microphone.list_microphone_names()
        return len(mics) > 0
    except Exception:
        return False
