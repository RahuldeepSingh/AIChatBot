"""
backends.py — chooses which chatbot backend to use.

A "backend" is any object with:
    - .bot_name   (str)
    - .get_response(user_input: str) -> str

Selection is controlled by the CHATBOT_BACKEND environment variable:
    rules  -> RuleEngine       (default; no API key needed)
    openai -> OpenAIBackend    (OpenAI via openai SDK; needs OPENAI_API_KEY)
    llm    -> LLMBackend       (Claude via anthropic SDK; needs ANTHROPIC_API_KEY)
"""

import os

from rule_engine import RuleEngine

_ENV_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")


def load_dotenv(path=_ENV_FILE):
    """Load KEY=value lines from a .env file into the environment.

    Minimal, dependency-free. Existing environment variables win (so an
    explicitly exported value overrides the file). Lines that are blank,
    comments (#), or lack '=' are ignored; surrounding quotes are stripped.
    """
    if not os.path.exists(path):
        return
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def get_backend(name=None):
    """Return a chatbot backend. `name` overrides the env var if given."""
    load_dotenv()  # pick up ANTHROPIC_API_KEY etc. from a .env file if present
    name = (name or os.environ.get("CHATBOT_BACKEND", "rules")).lower()

    if name == "openai":
        # Imported lazily so the rule-based path never needs `openai`.
        from openai_backend import OpenAIBackend
        return OpenAIBackend()

    if name == "llm":
        # Imported lazily so the rule-based path never needs `anthropic`.
        from llm_backend import LLMBackend
        return LLMBackend()

    return RuleEngine()
