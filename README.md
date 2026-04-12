# Winterest API

Backend REST API for the Winterest geography game.

## Prerequisites

- **Python 3**
- **MongoDB** — `brew tap mongodb/brew && brew install mongodb-community`

## First-Time Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
make dev_env
brew services start mongodb-community
make seed
```

## Daily Startup

```bash
source .venv/bin/activate
make start
```

The API runs at **http://127.0.0.1:8000**.

## Commands

| Command | What it does |
|---|---|
| `make dev_env` | Installs all dependencies (runtime + test/lint) |
| `make seed` | Seeds game data into local MongoDB (safe to re-run) |
| `make start` | Starts the Flask dev server on port 8000 |
| `make all_tests` | Runs lint + tests across all modules |

> **Re-seed** (`make seed`) only after a fresh setup or when `seed/seed_data.json` changes. MongoDB retains data between restarts. Seeding does not affect user accounts, scores, or friends.
