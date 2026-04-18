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
    for entry in history[-10:]:  # Keep last 10 turns for context window
        messages.append({'role': entry['role'], 'content': entry['content']})
    messages.append({'role': 'user', 'content': user_input})

    response = openai.ChatCompletion.create(
        model=os.getenv('OPENAI_MODEL', 'gpt-4o'),
        messages=messages,
        temperature=0.7
    )
    return response.choices[0].message['content'].strip()


def main():
    """Main REPL loop for J.A.R.V.I.S. 2.0."""
    logger.info('J.A.R.V.I.S. 2.0 initializing...')
    history = load_chat_history()
    kb_content = load_knowledgebase()
    system_prompt = build_system_prompt(kb_content)

    print('\nJ.A.R.V.I.S. 2.0 online. Type "exit" to quit.\n')

    while True:
        try:
            user_input = input('You: ').strip()
            if not user_input:
                continue
            if user_input.lower() in ('exit', 'quit', 'bye'):
                print('J.A.R.V.I.S.: Goodbye.')
                save_chat_history(history)
                break

            append_to_history(history, 'user', user_input)
            response = get_ai_response(user_input, history, system_prompt)
            append_to_history(history, 'assistant', response)
            save_chat_history(history)

            print(f'J.A.R.V.I.S.: {response}\n')

        except KeyboardInterrupt:
            print('\nJ.A.R.V.I.S.: Session interrupted. Saving history...')
            save_chat_history(history)
            break
        except Exception as e:
            logger.error(f'Unexpected error: {e}')


if __name__ == '__main__':
    main()
