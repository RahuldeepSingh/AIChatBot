#!/usr/bin/env python3
"""
bot.py — CLI chatbot for the AIChatBot project.

Backends (choose with the CHATBOT_BACKEND environment variable):
    rules  -> rule-based matching from rules.json      (default, no API key)
    llm    -> Claude-powered replies via the anthropic SDK (needs ANTHROPIC_API_KEY)

Examples:
    python3 bot.py                       # rule-based
    CHATBOT_BACKEND=llm python3 bot.py   # LLM-powered (needs key + `pip install anthropic`)
"""

import sys

from backends import get_backend

EXIT_COMMANDS = {"quit", "exit", "\\q"}


def main():
    try:
        bot = get_backend()
    except Exception as e:
        print(f"Error starting chatbot: {e}", file=sys.stderr)
        sys.exit(1)
    name = bot.bot_name

    print(f"{name}: Hi! I'm {name}. Type 'help' for what I can do, "
          f"or 'quit' to leave.")

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print(f"\n{name}: Goodbye!")
            break

        if not user_input:
            continue

        if user_input.lower() in EXIT_COMMANDS:
            print(f"{name}: Goodbye!")
            break

        print(f"{name}: {bot.get_response(user_input)}")


if __name__ == "__main__":
    main()
