# Winterest API

Backend REST API for the Winterest geography guessing game. Built with Flask, Flask-RESTX, and MongoDB.

### Prerequisites

- **Python 3.13+**
- **MongoDB** — `brew tap mongodb/brew && brew install mongodb-community`

### First-Time Setup

```bash
make setup
```

Creates `.venv/`, installs dependencies, starts MongoDB, and seeds game data. Safe to re-run.

### Daily Startup

```bash
make start
```

The API runs at **http://127.0.0.1:8000**. Auto-starts MongoDB if it's not already running.

---

### Layer Responsibilities

| Layer | Location | Role |
|-------|----------|------|
| **API** | `server/endpoints.py` | Route definitions, request parsing, response formatting. |
| **Query** | `<entity>/queries_<entity>.py` | Business logic, CRUD operations, validation, caching, and specialized queries (hints, aggregation, random selection). |
| **Hints** | `<entity>/hints.py` | Builds progressive hint sequences for game entities across 5 difficulty levels. |
| **DB Connect** | `data/db_connect.py` | MongoDB client management, generic CRUD helpers, retry logic (`@retry_mongo`), error handling (`@handle_errors`). |
| **Security** | `security/security.py` | Extensible ACL framework. |

### Key Patterns

- **Entity-per-package** — Each geographic entity (countries, states, cities, counties) has its own directory with queries, hints, and tests.
- **In-memory caching** — Query modules use a `@needs_cache` decorator for lazy-loaded caches, avoiding repeated DB reads.
- **Decorator-based DB management** — `@needs_db` auto-connects, `@retry_mongo()` retries on failures, `@handle_errors` normalizes PyMongo exceptions.

---

## Project Structure

```
Winterest/
├── server/
│   ├── endpoints.py           # All Flask routes
│   └── tests/                 # API endpoint tests
├── data/
│   └── db_connect.py          # MongoDB connection + generic CRUD
├── users/
│   └── queries_users.py       # Signup, login, user profiles, leaderboard
├── scores/
│   ├── queries_scores.py      # Score tracking, aggregation by period
│   └── tests/
├── friends/
│   └── queries_friends.py     # Bidirectional friend relationships
├── countries/
│   ├── queries_countries.py   # Country CRUD + validation
│   ├── hints.py               # Country hint builder (5 levels)
│   └── tests/
├── states/
│   ├── queries_states.py      # State CRUD + validation
│   ├── hints.py               # State hint builder (5 levels)
│   └── tests/
├── cities/
│   ├── queries_cities.py      # City CRUD + validation
│   ├── hints.py               # City hint builder (5 levels)
│   └── tests/
├── counties/
│   ├── queries_counties.py    # County CRUD + validation
│   └── tests/
├── prompts/
│   └── queries_prompts.py     # Quiz prompt questions
├── puzzles/
│   └── queries_puzzles.py     # Puzzle game data
├── security/
│   └── security.py            # ACL framework (extensible)
├── seed/
│   └── seed_data.json         # Seed data
├── scripts/
│   └── load_script.py         # DB seeding via upsert
├── examples/
│   ├── form.py                # Interactive API client / form builder
│   └── form_filler.py         # Form field descriptors
├── .github/workflows/
│   └── main.yml               # CI: lint + test on push/PR to master
├── makefile                   # Build automation
├── requirements.txt           # Production deps
├── requirements-dev.txt       # Dev deps (pytest, flake8, etc.)
├── deploy.sh                  # PythonAnywhere deploy script
└── rebuild.sh                 # Remote rebuild script
```

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Language | Python 3.13 |
| Web Framework | Flask 2.3.3 |
| API Framework | Flask-RESTX 1.1.0 |
| Database | MongoDB (local or Atlas) |
| DB Driver | PyMongo |
| Password Hashing | bcrypt 5.0.0 |
| CORS | Flask-CORS |
| CI/CD | GitHub Actions |
| Hosting | PythonAnywhere |
| Linting | flake8 |
| Testing | pytest + pytest-cov |

---

## API Endpoints

### Auth

| Method | Path | Description |
|--------|------|-------------|
| POST | `/signup` | Register a new user (email, username, password) |
| POST | `/login` | Authenticate (email or username + password) |

### Geographic Entities (CRUD for each)

Each entity type (`/countries`, `/states`, `/cities`, `/counties`) supports:

| Method | Path | Description |
|--------|------|-------------|
| GET | `/<entity>` | List all (countries/states/cities include computed hints) |
| POST | `/<entity>` | Create new entity |
| GET | `/<entity>/<id>` | Get one by ID |
| PUT | `/<entity>/<id>` | Update by ID |
| DELETE | `/<entity>/<id>` | Delete by ID |

### Game Content

| Method | Path | Description |
|--------|------|-------------|
| GET | `/prompts?type=<type>` | Get quiz prompt questions |
| GET | `/quiz/questions?type=<type>&count=<n>` | Get N random quiz questions |
| GET | `/puzzles?entity_type=<type>` | Get puzzles by entity type |
| GET | `/puzzle/quiz?entity_type=<type>&count=<n>` | Get N random puzzles |

### Scores & Leaderboard

| Method | Path | Description |
|--------|------|-------------|
| GET | `/scores` | All scores |
| POST | `/scores` | Submit a new score |
| GET | `/scores/aggregated?period=<all\|week\|month>` | Leaderboard (sum scores by player, filtered by period) |
| GET | `/leaderboard/filters` | Available leaderboard filter options |

### Social

| Method | Path | Description |
|--------|------|-------------|
| GET | `/friends?user_id=<id>` | Get user's friend list |
| POST | `/friends` | Add friend (by email) |
| DELETE | `/friends` | Remove friend |
| GET | `/scores/friends?user_id=<id>` | Scores for user + friends |
| GET | `/scores/friends/aggregated?user_id=<id>&period=<period>` | Friend group leaderboard |

### Utility

| Method | Path | Description |
|--------|------|-------------|
| GET | `/hello`, `/health` | Health checks |
| GET | `/stats` | Entity counts across all collections |
| GET | `/endpoints` | Lists all available API endpoints |
| POST | `/echo` | Echoes back POST body |
| GET | `/dev/logs?lines=<n>` | View server logs (dev only) |

Full interactive docs available at **http://127.0.0.1:8000/** (Swagger UI).

---

## Database Schema

Database name: **seDB** (MongoDB)

### users

| Field | Type | Description |
|-------|------|-------------|
| id | uuid | Primary key |
| email | string | Normalized email |
| username | string | Alphanumeric + underscore |
| password | string | Bcrypt hash |
| friends | array | List of friend user IDs |
| score | int | Accumulated total score |
| games_played | int | Total games completed |

### scores

| Field | Type | Description |
|-------|------|-------------|
| id | uuid | Primary key |
| user_id | uuid | Foreign key to users |
| player | string | Player name (or "anonymous") |
| score | int | Points earned |
| guesses_used | int | Guesses before correct answer |
| entity_type | string | "cities", "states", or "countries" |
| timestamp | ISO-8601 | When score was recorded |

### friends

| Field | Type | Description |
|-------|------|-------------|
| id | uuid | Primary key |
| user_id | uuid | One side of friendship |
| friend_id | uuid | Other side (bidirectional — two records per friendship) |

### countries

| Field | Type | Description |
|-------|------|-------------|
| country_id | string | Unique code (e.g., "US") |
| name | string | Country name |
| population | int | Population |
| continent | string | Continent |
| capital | string | Capital city |
| gdp, area, founded, president, flag_color, language, climate | string | Hint data |

### states

| Field | Type | Description |
|-------|------|-------------|
| id | uuid | Primary key |
| name | string | State name |
| state_code | string | 2-letter code |
| population | int | Population |
| capital, area, founded, gdp, governor, climate, state_bird | string | Hint data |

### cities

| Field | Type | Description |
|-------|------|-------------|
| id | uuid | Primary key |
| name | string | City name |
| state, state_code | string | Parent state |
| population, area, founded, mayor, gdp, climate, nickname | string | Hint data |

### counties

| Field | Type | Description |
|-------|------|-------------|
| id | uuid | Primary key |
| name | string | County name |
| state, state_code | string | Parent state |
| population | int | Population |
| area, founded, county_seat | string | Descriptive data |

### prompts / puzzles

Both store quiz content with `entity_type`, `answer`, `approved` flag, and associated hint/asset fields.

---

## Game Mechanics

### How the Game Works

Players guess a geographic entity (country, state, or city) based on progressive hints. Fewer guesses = higher score.

### Hint System (5 Difficulty Levels)

Hints are revealed one level at a time after each incorrect guess, from hardest to easiest:

**Countries:**

| Level | Hints |
|-------|-------|
| 5 (hardest) | Area, Founded year |
| 4 | Population, Climate |
| 3 | Flag color, GDP |
| 2 | President, Language |
| 1 (easiest) | Continent, Capital |

**States:**

| Level | Hints |
|-------|-------|
| 5 (hardest) | GDP, State bird |
| 4 | Population, Climate |
| 3 | Area, Statehood date |
| 2 | Governor, Capital |
| 1 (easiest) | State code |

**Cities:**

| Level | Hints |
|-------|-------|
| 5 (hardest) | Founded, GDP |
| 4 | Population, Climate |
| 3 | Area |
| 2 | Mayor, Nickname |
| 1 (easiest) | State |

Hints within each level are randomly selected for variety.

### Scoring

- Score is recorded with `guesses_used` count
- Each completed game updates the user's total `score` and `games_played`
- Leaderboards aggregate scores across configurable time periods (all-time, past month, past week)

### Social Features

- Add friends by email (bidirectional relationship)
- View friend-only leaderboard
- Compare scores within your friend group

---

## Authentication

Currently uses basic email/username + bcrypt password authentication:

1. **Signup** (`POST /signup`) — Validates fields, hashes password with bcrypt, creates user
2. **Login** (`POST /login`) — Looks up user by email or username, verifies password hash

---

## Testing

```bash
make all_tests     # Runs flake8 lint + pytest across all modules
```

Tests live in `<module>/tests/` directories. The test suite uses:

- **pytest** for test execution
- **unittest.mock** for mocking DB calls
- **Flask test client** for HTTP endpoint testing

### CI/CD

GitHub Actions (`.github/workflows/main.yml`) runs on every push/PR to `master`

---

## Deployment

### PythonAnywhere

The production API is hosted on PythonAnywhere. Deployment is automated via:

```bash
./deploy.sh        # SSHs into PythonAnywhere, runs rebuild
```

The `rebuild.sh` script on the remote server pulls the latest code and reloads the web app.

### Manual Deploy

```bash
make prod          # Runs all tests, then pushes to master
```

---

## Make Commands

| Command | Description |
|---------|-------------|
| `make setup` | One-time setup: venv + deps + MongoDB + seed |
| `make start` | Start Flask dev server on port 8000 |
| `make seed` | Re-seed game data from `seed/seed_data.json` |
| `make all_tests` | Lint + tests across all modules |
| `make dev_env` | Create venv + install deps only (used by CI) |
| `make clean` | Remove `.venv/` directory |
| `make prod` | Run tests + push to master |
