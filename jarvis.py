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
        'and answering general questions.'
    )
    if kb_content:
        base_prompt += f'\n\nKnowledgebase Context:\n{kb_content}'
    return base_prompt


def get_ai_response(user_input: str, history: list, system_prompt: str) -> str:
    """
    Placeholder for AI response generation.
    Replace with actual LLM API call (e.g., OpenAI, Gemini).
    """
    import openai

    openai.api_key = os.getenv('OPENAI_API_KEY')
    messages = [{'role': 'system', 'content': system_prompt}]
    for entry in history[-CONTEXT_WINDOW_TURNS:]:  # Keep last N turns for context window
        messages.append({'role': entry['role'], 'content': entry['content']})
    messages.append({'role': 'user', 'content': user_input})

    response = openai.ChatCompletion.create(
        model=os.gete