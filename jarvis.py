#!/usr/bin/env python3
"""
J.A.R.V.I.S. 2.0 - Main Entry Point
Just A Rather Very Intelligent System

Fork of adam104504/J.A.R.V.I.S.2.0
"""

import os
import json
import logging
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('DATA/jarvis.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

CHAT_HISTORY_PATH = 'DATA/chat_history.json'
KNOWLEDGEBASE_PATH = 'DATA/KNOWLEDGEBASE/disaster_data_converted.md'

# Keep last N turns for context window - increase if you want more memory,
# but be mindful of token limits (gpt-3.5-turbo: ~4k, gpt-4: ~8k)
# Bumped from 20 to 30 - I'm using gpt-4 and want longer conversation memory
# Bumped again to 50 - conversations were getting cut off too early
# Dropped back to 40 - 50 was hitting token limits on longer messages
# Dropped to 30 - switched back to gpt-3.5-turbo to save on API costs
# Dropped to 20 - 30 was still occasionally hitting limits with the knowledgebase injected
CONTEXT_WINDOW_TURNS = 20


def load_chat_history() -> list:
    """Load existing chat history from JSON file."""
    if os.path.exists(CHAT_HISTORY_PATH):
        try:
            with open(CHAT_HISTORY_PATH, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f'Failed to load chat history: {e}')
    return []


def save_chat_history(history: list) -> None:
    """Persist chat history to JSON file."""
    try:
        with open(CHAT_HISTORY_PATH, 'w') as f:
            json.dump(history, f, indent=2)
    except IOError as e:
        logger.error(f'Failed to save chat history: {e}')


def append_to_history(history: list, role: str, content: str) -> None:
    """Append a new message entry to the chat history."""
    history.append({
        'role': role,
        'content': content,
        'timestamp': datetime.utcnow().isoformat()
    })


def load_knowledgebase() -> str:
    """Load the knowledgebase markdown content as context."""
    if os.path.exists(KNOWLEDGEBASE_PATH):
        try:
            with open(KNOWLEDGEBASE_PATH, 'r') as f:
                return f.read()
        except IOError as e:
            logger.error(f'Failed to load knowledgebase: {e}')
    return ''


def build_system_prompt(kb_content: str) -> str:
    """Build the system prompt, optionally injecting knowledgebase data."""
    base_prompt = (
        'You are J.A.R.V.I.S. 2.0, an advanced AI assistant. '
        'You are helpful, concise, and precise. '
        'You can assist with information retrieval, sending emails, '
        'and answering general questions. '
        # Personal preference: I find the default responses a bit terse,
        # so nudging it to elaborate slightly when explaining concepts.
        'When explaining technical concepts, provide a brief example if it aids clarity. '
        # Prefer metric units by defa
