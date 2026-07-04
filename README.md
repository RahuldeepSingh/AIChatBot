# AIChatBot 🤖

A learning project for building chatbots, growing through three working modes:

1. **Phase 1 — Rule-based bot** (keyword matching, zero dependencies) ✅
2. **Phase 2 — Web UI** (browser chat, Flask) ✅
3. **Phase 3 — LLM-powered bot** (Claude *or* OpenAI) ✅

All three share one rule/response engine and a common backend interface, so the
same code powers the terminal and the browser, in either rule-based or
AI-powered mode.

See [`chatbot-research.md`](chatbot-research.md) (or the styled
[`chatbot-research.html`](chatbot-research.html)) for the full breakdown of
chatbot types.

---

## Table of Contents

- [How it works](#how-it-works)
- [Tech stack](#tech-stack)
- [Libraries & APIs](#libraries--apis)
- [Project structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Setup & installation](#setup--installation)
  - [macOS](#macos)
  - [Windows](#windows)
  - [Linux](#linux)
- [Running the bot](#running-the-bot)
  - [Phase 1 — rule-based CLI](#phase-1--rule-based-cli)
  - [Phase 2 — web UI](#phase-2--web-ui)
  - [Phase 3 — LLM-powered (Claude or OpenAI)](#phase-3--llm-powered-claude-or-openai)
  - [Switching backend live (web UI)](#switching-backend-live-web-ui)
- [Configuration](#configuration)
- [Customizing the rules](#customizing-the-rules)
- [Troubleshooting](#troubleshooting)
- [Roadmap](#roadmap)

---

## How it works

The project has a small, layered design:

- **`rule_engine.py`** — loads `rules.json` and matches keywords → responses.
- **`llm_backend.py`** — talks to **Claude** via the Anthropic SDK.
- **`openai_backend.py`** — talks to **OpenAI** via the OpenAI SDK.
- **`backends.py`** — picks which backend to use from an env var, and loads a
  `.env` file if present.
- **`bot.py`** — terminal chat loop.
- **`app.py`** — Flask web server + browser chat UI (`templates/index.html`).

Both `bot.py` and `app.py` call `backends.get_backend()`, so you switch between
rule-based, Claude, and OpenAI replies with a single environment variable
(`CHATBOT_BACKEND`) — no code changes. In the **web UI** you can also switch
backends **live from a dropdown**, with no restart (see below).

---

## Tech stack

| Layer         | Technology                          | Used in       |
|---------------|-------------------------------------|---------------|
| Language      | **Python 3.10+** (tested on 3.14)   | all phases    |
| Rule matching | `re`, `json`, `random` (stdlib)     | Phase 1       |
| Web server    | **Flask**                           | Phase 2       |
| Web UI        | HTML + CSS + vanilla JS             | Phase 2       |
| LLM           | **Claude** (`anthropic` SDK) **or OpenAI** (`openai` SDK) | Phase 3 |

## Libraries & APIs

- **Phase 1** uses **only the Python standard library** — nothing to install.
- **Phase 2** adds **[Flask](https://pypi.org/project/flask/)**.
- **Phase 3** supports **two providers** — pick one:
  - **Claude** — [`anthropic`](https://pypi.org/project/anthropic/) SDK +
    `ANTHROPIC_API_KEY`. Default model `claude-opus-4-8`.
    ([console.anthropic.com](https://console.anthropic.com/))
  - **OpenAI** — [`openai`](https://pypi.org/project/openai/) SDK +
    `OPENAI_API_KEY`. Default model `gpt-4o-mini`.
    ([platform.openai.com](https://platform.openai.com/api-keys))

Phase 2 and 3 dependencies are listed in [`requirements.txt`](requirements.txt).
API keys can go in a **`.env`** file (see [`.env.example`](.env.example)) — it's
gitignored and loaded automatically, so keys never touch the code or your shell
history.

---

## Project structure

```
AIChatBot/
├── bot.py                  # CLI chat loop (rules or LLM)
├── app.py                  # Flask web app (rules or LLM)
├── backends.py             # Chooses the backend from CHATBOT_BACKEND; loads .env
├── rule_engine.py          # Rule loading + keyword matching
├── llm_backend.py          # Claude-powered backend (Anthropic SDK)
├── openai_backend.py       # OpenAI-powered backend (OpenAI SDK)
├── rules.json              # Editable keyword -> response rules
├── requirements.txt        # Phase 2/3 dependencies
├── .env.example            # Template for API keys (copy to .env)
├── templates/
│   └── index.html          # Browser chat UI
├── README.md               # This file
├── chatbot-research.md     # Research: the 5 types of chatbots
├── chatbot-research.html   # Same research, styled for the browser
└── docs/
    └── project-context.md  # Project context, decisions & conversation log
```

---

## Prerequisites

- **Python 3.10 or newer** (3.14 recommended)
- **git** (only to clone)
- **An API key** — *Phase 3 only*. Either a **Claude** key from
  [console.anthropic.com](https://console.anthropic.com/) or an **OpenAI** key
  from [platform.openai.com](https://platform.openai.com/api-keys).

Check what you have:

```bash
python3 --version     # or: python --version   (Windows)
git --version
```

---

## Setup & installation

### Clone the project (all platforms)

```bash
git clone <repository-url> AIChatBot
cd AIChatBot
```

**Phase 1 needs no installation** — if you only want the rule-based CLI, skip
straight to [Running the bot](#phase-1--rule-based-cli).

For **Phase 2 or 3**, create a virtual environment and install the
dependencies. Per-OS instructions follow.

---

### macOS

1. **Install Python 3** if needed:
   ```bash
   brew install python          # Homebrew
   # or download from https://www.python.org/downloads/macos/
   ```
2. **Create a virtual environment and install dependencies** (Phase 2/3):
   ```bash
   cd /path/to/AIChatBot
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

---

### Windows

1. **Install Python** from
   [python.org/downloads/windows](https://www.python.org/downloads/windows/) —
   tick **"Add python.exe to PATH"** on the first screen.
   *(Or: `winget install Python.Python.3.12`.)*
2. **Create a virtual environment and install dependencies** (Phase 2/3), in
   PowerShell:
   ```powershell
   cd C:\path\to\AIChatBot
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```

> If `python` opens the Microsoft Store, install from python.org, or use `py`.

---

### Linux

1. **Install Python 3** if needed:
   ```bash
   sudo apt update && sudo apt install python3 python3-venv   # Debian/Ubuntu
   # sudo dnf install python3           # Fedora
   # sudo pacman -S python              # Arch
   ```
2. **Create a virtual environment and install dependencies** (Phase 2/3):
   ```bash
   cd /path/to/AIChatBot
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

---

## Running the bot

> If you created a virtual environment, activate it first
> (`source .venv/bin/activate`, or `.venv\Scripts\activate` on Windows).
> On macOS/Linux use `python3`; on Windows use `python` (or `py`).

### Phase 1 — rule-based CLI

No dependencies required.

```bash
python3 bot.py
```

Type `help` to see what it can do, and `quit` to leave.

```
RuleBot: Hi! I'm RuleBot. Type 'help' for what I can do, or 'quit' to leave.
You: hello
RuleBot: Hi there! What can I do for you?
You: what types of chatbots are there
RuleBot: There are 5 main types: 1) Rule-based, 2) LLM-powered, ...
You: quit
RuleBot: Goodbye!
```

### Phase 2 — web UI

Runs the browser chat interface (rule-based by default):

```bash
python app.py
```

Then open **http://127.0.0.1:5000** in your browser.

### Phase 3 — LLM-powered (Claude or OpenAI)

Pick a provider and supply its key. The `CHATBOT_BACKEND` value selects it:

| Provider | `CHATBOT_BACKEND` | Key variable        | Default model    |
|----------|-------------------|---------------------|------------------|
| Claude   | `llm`             | `ANTHROPIC_API_KEY` | `claude-opus-4-8`|
| OpenAI   | `openai`          | `OPENAI_API_KEY`    | `gpt-4o-mini`    |

#### Recommended: use a `.env` file

Copy the template and fill in one key:

```bash
cp .env.example .env
```

Then edit `.env`, e.g. for OpenAI:

```
OPENAI_API_KEY=sk-proj-...your-key...
CHATBOT_BACKEND=openai
```

…or for Claude:

```
ANTHROPIC_API_KEY=sk-ant-...your-key...
CHATBOT_BACKEND=llm
```

Now just run either interface — the key and backend are picked up automatically:

```bash
python3 bot.py     # terminal, AI-powered
python app.py      # browser, AI-powered  (http://127.0.0.1:5000)
```

#### Alternative: environment variables

**macOS / Linux (OpenAI shown):**
```bash
export OPENAI_API_KEY=sk-proj-...
CHATBOT_BACKEND=openai python app.py       # or: python3 bot.py
```

**Windows (PowerShell, Claude shown):**
```powershell
$env:ANTHROPIC_API_KEY = "sk-ant-..."
$env:CHATBOT_BACKEND = "llm"
python app.py        # or: python bot.py
```

If the key is missing or invalid, the bot tells you exactly what's wrong instead
of crashing.

> 🔒 **Never commit or paste your API key.** Put it only in `.env` (gitignored).
> If a key is ever exposed, revoke it and generate a new one.

### Switching backend live (web UI)

In the browser UI there's a **dropdown in the top-right of the header** to switch
between **Rule based**, **OpenAI**, and **Anthropic (Claude)** on the fly — no
restart needed. When you switch:

- the bot name, avatar, and "Running on …" label update instantly, and a small
  note appears in the chat (e.g. *"— Running on Rule based —"*);
- each backend keeps its **own conversation history**, so switching back resumes
  where you left off;
- if a backend can't start (e.g. you pick Claude but no `ANTHROPIC_API_KEY` is
  set), the switch fails gracefully with a message and the current backend stays
  active.

Only backends whose key is configured will actually connect — Rule based always
works with no key.

---

## Configuration

Behavior is controlled with environment variables (in `.env` or your shell) —
no code edits needed:

| Variable            | Default                     | What it does                                          |
|---------------------|-----------------------------|-------------------------------------------------------|
| `CHATBOT_BACKEND`   | `rules`                     | `rules` (keyword bot), `llm` (Claude), or `openai`     |
| `ANTHROPIC_API_KEY` | *(none)*                    | Your Claude API key — required for `llm`               |
| `OPENAI_API_KEY`    | *(none)*                    | Your OpenAI API key — required for `openai`            |
| `CHATBOT_MODEL`     | per provider*               | Which model to use in `llm` / `openai` mode            |
| `CHATBOT_BOT_NAME`  | `Claude` / `Assistant`      | Display name in the UI                                 |
| `PORT`              | `5000`                      | Port for the web app                                  |

\* `CHATBOT_MODEL` defaults to `claude-opus-4-8` for `llm` and `gpt-4o-mini` for `openai`.

> **Cost note:** for cheaper, faster replies use `CHATBOT_MODEL=claude-haiku-4-5`
> (Claude) or `CHATBOT_MODEL=gpt-4o-mini` (OpenAI). For higher quality, try
> `claude-opus-4-8` or `gpt-4o`.

---

## Customizing the rules

Edit [`rules.json`](rules.json) — no Python needed. Each rule:

```json
{
  "intent": "greeting",
  "patterns": ["\\bhi\\b", "\\bhello\\b", "\\bhey\\b"],
  "responses": ["Hello! How can I help you today?", "Hi there!"]
}
```

- **`patterns`** — regular expressions; if any matches (case-insensitive), the rule fires.
- **`responses`** — one is picked at random.

Copy a block, change the patterns and responses, and save.

---

## Troubleshooting

| Problem                                            | Fix                                                                              |
|----------------------------------------------------|----------------------------------------------------------------------------------|
| `command not found: python3`                       | Python isn't installed / not on PATH — see your OS's setup section.               |
| Windows: `python` opens the Microsoft Store        | Install from python.org (tick "Add to PATH"), or use `py`.                        |
| `ModuleNotFoundError: No module named 'flask'`     | Activate the venv and run `pip install -r requirements.txt`.                      |
| `No Claude credentials found`                      | Set `ANTHROPIC_API_KEY` (in `.env`) before running in `llm` mode.                 |
| `No OpenAI credentials found`                      | Set `OPENAI_API_KEY` (in `.env`) before running in `openai` mode.                 |
| `Authentication failed` in LLM/OpenAI mode         | Key is wrong, expired, or revoked. Check the key value — a common slip is a stray character (e.g. `ssk-` instead of `sk-`). Also confirm your account has credit. |
| `.env` changes not taking effect                   | The key is read at startup — restart the server/CLI after editing `.env`.         |
| `Error: rules file not found`                      | Run from inside the project folder so it can find `rules.json`.                   |
| Port 5000 already in use                           | Run with a different port: `PORT=5001 python app.py`.                             |

---

## Roadmap

1. **Phase 1 — Rule-based CLI bot** ✅
2. **Phase 2 — Web UI** ✅
3. **Phase 3 — LLM-powered replies (Claude or OpenAI)** ✅
4. **Phase 4 — Retrieval (RAG) + tools/agent actions** (next)

---

*Project docs and decision history live in [`docs/project-context.md`](docs/project-context.md).*
