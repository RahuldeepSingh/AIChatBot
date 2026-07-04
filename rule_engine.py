"""
rule_engine.py — shared rule-matching logic for the AIChatBot project.

Both the CLI bot (bot.py) and the web app (app.py) import this module so the
rule-matching behavior stays in one place.
"""

import json
import os
import random
import re

RULES_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "rules.json")


class RuleEngine:
    """Loads keyword->response rules and returns replies for user messages."""

    def __init__(self, rules_path=RULES_FILE):
        self.settings, self.rules = self._load(rules_path)
        self.bot_name = self.settings.get("bot_name", "Bot")
        self.fallback = self.settings.get(
            "fallback", "Sorry, I didn't understand that."
        )
        self.status_label = "Running on Rule based"

    @staticmethod
    def _load(path):
        """Load and validate the rules file, returning (settings, rules)."""
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Rules file not found at {path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"rules.json is not valid JSON: {e}")

        settings = data.get("settings", {})
        rules = data.get("rules", [])

        # Pre-compile each rule's patterns once for efficiency.
        for rule in rules:
            rule["_compiled"] = [
                re.compile(p, re.IGNORECASE) for p in rule.get("patterns", [])
            ]
        return settings, rules

    def match(self, user_input):
        """Return the first rule whose any pattern matches, else None."""
        for rule in self.rules:
            for pattern in rule["_compiled"]:
                if pattern.search(user_input):
                    return rule
        return None

    def get_response(self, user_input):
        """Return the bot's reply string for a given user input."""
        rule = self.match(user_input)
        if rule and rule.get("responses"):
            return random.choice(rule["responses"])
        return self.fallback
