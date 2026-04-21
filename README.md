# Winterest API

Backend REST API for the Winterest geography game.

## Prerequisites

- **Python 3**
- **MongoDB** — `brew tap mongodb/brew && brew install mongodb-community`

## First-Time Setup

```bash
make setup
```

Creates `.venv/`, installs dependencies, starts MongoDB, and seeds game data. Safe to re-run.

## Daily Startup

```bash
make start
```

The API runs at **http://127.0.0.1:8000**. Auto-starts MongoDB if it's not already running.

## Commands

| Command | What it does |
|---|---|
| `make setup` | One-shot: venv + deps + Mongo + seed (idempotent) |
| `make start` | Starts the Flask dev server on port 8000 |
| `make seed` | Re-seeds game data into local MongoDB |
| `make all_tests` | Runs lint + tests across all modules |
| `make clean` | Removes the `.venv/` directory |

> **Re-seed** (`make seed`) only after a fresh setup or when `seed/seed_data.json` changes. MongoDB retains data between restarts. Seeding does not affect user accounts, scores, or friends.

## Environment

Local development needs no environment configuration. For cloud MongoDB or custom seed URIs, copy [`.env.example`](.env.example) to `.env` and fill in the relevant values.
