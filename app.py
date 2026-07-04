#!/usr/bin/env python3
"""
app.py — Phase 2/3 web UI for the AIChatBot project.

Serves a browser chat interface. The backend (rule-based, Claude, or OpenAI) can
be chosen at startup with CHATBOT_BACKEND, and also switched live from the UI via
the /switch endpoint — no restart needed.

Run:
    python app.py            # starts on the CHATBOT_BACKEND from .env (or rules)
Then open http://127.0.0.1:5000 in your browser.
"""

import os

from flask import Flask, jsonify, render_template, request

from backends import get_backend

app = Flask(__name__)

# Friendly labels for the UI selector -> internal backend keys.
BACKEND_OPTIONS = [
    {"key": "rules", "label": "Rule based"},
    {"key": "openai", "label": "OpenAI"},
    {"key": "llm", "label": "Anthropic (Claude)"},
]
_VALID_KEYS = {b["key"] for b in BACKEND_OPTIONS}

# Each backend is created once and cached, so switching back and forth keeps
# each one's own conversation history.
_cache = {}
_current = None


def use_backend(key):
    """Return the backend for `key`, creating and caching it if needed.

    Raises whatever the backend constructor raises (e.g. a missing API key),
    and leaves the current selection unchanged if creation fails.
    """
    global _current
    if key not in _cache:
        _cache[key] = get_backend(key)  # may raise (e.g. missing credentials)
    _current = key
    return _cache[key]


def current():
    return _cache[_current]


# Start on whatever CHATBOT_BACKEND requests, falling back to the always-
# available rule-based bot if that backend can't start (e.g. no API key).
_start = os.environ.get("CHATBOT_BACKEND", "rules").lower()
if _start not in _VALID_KEYS:
    _start = "rules"
try:
    use_backend(_start)
except Exception:
    use_backend("rules")


@app.route("/")
def index():
    bot = current()
    return render_template(
        "index.html",
        bot_name=bot.bot_name,
        status_label=getattr(bot, "status_label", ""),
        backends=BACKEND_OPTIONS,
        current_backend=_current,
    )


@app.route("/switch", methods=["POST"])
def switch():
    data = request.get_json(silent=True) or {}
    key = (data.get("backend") or "").lower()
    if key not in _VALID_KEYS:
        return jsonify({"ok": False, "error": "Unknown backend."}), 400
    try:
        bot = use_backend(key)
    except Exception as e:
        # Current backend is left unchanged; report why the switch failed.
        return jsonify({"ok": False, "error": str(e)}), 200
    return jsonify({
        "ok": True,
        "bot_name": bot.bot_name,
        "status_label": getattr(bot, "status_label", ""),
    })


@app.route("/chat", methods=["POST"])
def chat():
    bot = current()
    data = request.get_json(silent=True) or {}
    message = (data.get("message") or "").strip()
    if not message:
        return jsonify({"reply": "Please type a message."}), 400
    try:
        reply = bot.get_response(message)
    except Exception as e:
        return jsonify({"reply": f"Something went wrong: {e}"}), 500
    return jsonify({"reply": reply, "bot_name": bot.bot_name})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="127.0.0.1", port=port, debug=True)
