"""
openai_backend.py — OpenAI-powered backend for the AIChatBot project.

Uses OpenAI's Chat Completions API via the official `openai` Python SDK.
Exposes the same interface as the other backends (`.bot_name` +
`.get_response(text)`) so it drops into the CLI (bot.py) and web app (app.py).

Requirements:
    pip install openai            (already in requirements.txt)
    OPENAI_API_KEY in your .env   (or exported in the environment)

Environment variables:
    OPENAI_API_KEY      your OpenAI API key (required)
    CHATBOT_MODEL       model id (default: gpt-4o-mini)
    CHATBOT_BOT_NAME    display name (default: Assistant)
"""

import os

import openai
from openai import OpenAI

DEFAULT_MODEL = os.environ.get("CHATBOT_MODEL", "gpt-4o-mini")

SYSTEM_PROMPT = (
    "You are a friendly, helpful chatbot built as part of a learning "
    "project called AIChatBot. Keep replies clear and reasonably concise "
    "unless the user asks for detail."
)


class OpenAIBackend:
    """An OpenAI-powered conversational backend with multi-turn memory."""

    def __init__(self, model=DEFAULT_MODEL, system=SYSTEM_PROMPT):
        if not os.environ.get("OPENAI_API_KEY"):
            raise RuntimeError(
                "No OpenAI credentials found. Set OPENAI_API_KEY in your .env "
                "file (or the environment) to use the OpenAI backend.")

        # The SDK reads OPENAI_API_KEY from the environment. No key is hardcoded.
        self.client = OpenAI()
        self.model = model
        self.bot_name = os.environ.get("CHATBOT_BOT_NAME", "Assistant")
        self.status_label = f"Running on Open AI ({self.model})"
        # Chat Completions is stateless, so we track history ourselves. The
        # system prompt is the first message in the list.
        self.messages = [{"role": "system", "content": system}]

    def get_response(self, user_input):
        """Send the user's message (with history) to OpenAI and return the reply."""
        self.messages.append({"role": "user", "content": user_input})

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=self.messages,
                max_tokens=1024,
            )
        except openai.AuthenticationError:
            self.messages.pop()
            return ("Authentication failed. Set a valid OPENAI_API_KEY and "
                    "try again.")
        except openai.RateLimitError:
            self.messages.pop()
            return ("I'm being rate limited (or the account is out of "
                    "credit). Please check your OpenAI plan and retry.")
        except openai.APIError as e:
            self.messages.pop()
            return f"Sorry, the OpenAI API returned an error: {e}"
        except Exception as e:
            self.messages.pop()
            return f"Sorry, something went wrong talking to OpenAI: {e}"

        reply = (response.choices[0].message.content or "").strip()
        if not reply:
            reply = "(no response)"

        self.messages.append({"role": "assistant", "content": reply})
        return reply
