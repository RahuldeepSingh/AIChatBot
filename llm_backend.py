"""
llm_backend.py — Phase 3 LLM-powered backend for the AIChatBot project.

Uses Anthropic's Claude via the official `anthropic` Python SDK. Exposes the
same interface as the rule engine (`.bot_name` + `.get_response(text)`) so it
drops into the CLI (bot.py) and web app (app.py) with no other changes.

Requirements:
    pip install anthropic          (already in requirements.txt)
    export ANTHROPIC_API_KEY=...   (your Claude API key)

Environment variables:
    ANTHROPIC_API_KEY   your API key (required)
    CHATBOT_MODEL       model id (default: claude-opus-4-8)
    CHATBOT_BOT_NAME    display name (default: Claude)
"""

import os

import anthropic

DEFAULT_MODEL = os.environ.get("CHATBOT_MODEL", "claude-opus-4-8")

SYSTEM_PROMPT = (
    "You are a friendly, helpful chatbot built as Phase 3 of a learning "
    "project called AIChatBot. Keep replies clear and reasonably concise "
    "unless the user asks for detail."
)


class LLMBackend:
    """A Claude-powered conversational backend with multi-turn memory."""

    def __init__(self, model=DEFAULT_MODEL, system=SYSTEM_PROMPT):
        # Fail early with a clear message if there's no way to authenticate,
        # instead of a cryptic error on the first message.
        if not (os.environ.get("ANTHROPIC_API_KEY")
                or os.environ.get("ANTHROPIC_AUTH_TOKEN")):
            raise RuntimeError(
                "No Claude credentials found. Set the ANTHROPIC_API_KEY "
                "environment variable to use the LLM backend.\n"
                "  export ANTHROPIC_API_KEY=sk-ant-...")

        # The SDK resolves credentials from ANTHROPIC_API_KEY. No key is
        # hardcoded.
        self.client = anthropic.Anthropic()
        self.model = model
        self.system = system
        self.bot_name = os.environ.get("CHATBOT_BOT_NAME", "Claude")
        self.status_label = f"Running on Anthropic ({self.model})"
        # The Messages API is stateless, so we track history ourselves.
        self.messages = []

    def get_response(self, user_input):
        """Send the user's message (with history) to Claude and return the reply."""
        self.messages.append({"role": "user", "content": user_input})

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                system=self.system,
                messages=self.messages,
            )
        except anthropic.AuthenticationError:
            # Roll back the unanswered turn so history stays consistent.
            self.messages.pop()
            return ("Authentication failed. Set a valid ANTHROPIC_API_KEY "
                    "environment variable and try again.")
        except anthropic.RateLimitError:
            self.messages.pop()
            return "I'm being rate limited right now. Please wait a moment and retry."
        except anthropic.APIError as e:
            self.messages.pop()
            return f"Sorry, the API returned an error: {e}"
        except Exception as e:
            self.messages.pop()
            return f"Sorry, something went wrong talking to Claude: {e}"

        # Collect the text from the response content blocks.
        reply = "".join(
            block.text for block in response.content if block.type == "text"
        ).strip()

        if not reply:
            reply = "(no response)"

        self.messages.append({"role": "assistant", "content": reply})
        return reply
