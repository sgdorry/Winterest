include common.mk

VENV        := .venv
PY          := $(VENV)/bin/python
PIP         := $(VENV)/bin/pip
FLASK       := $(VENV)/bin/flask
REQS        := requirements.txt requirements-dev.txt
STAMP       := $(VENV)/.installed
export PYTHONPATH := $(CURDIR)
export PATH := $(CURDIR)/$(VENV)/bin:$(PATH)

# Our directories
API_DIR = server
DB_DIR = data
SEC_DIR = security
STATES_DIR = states
COUNTRIES_DIR = countries
CITIES_DIR = cities
SCORES_DIR = scores
USERS_DIR = users
FRIENDS_DIR = friends
PROMPTS_DIR = prompts
REQ_DIR = .

.PHONY: setup start seed mongo-up dev_env all_tests docs prod github clean FORCE

FORCE:

setup: $(STAMP) mongo-up seed
	@echo "Setup complete. Run: make start"

start: $(STAMP) mongo-up
	FLASK_ENV=development DEBUG=1 \
	$(FLASK) --app server.endpoints run --debug --host=127.0.0.1 --port=8000

seed: $(STAMP) mongo-up
	$(PY) -m scripts.load_script

$(STAMP): $(REQS)
	@test -d $(VENV) || python3 -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements-dev.txt
	@touch $(STAMP)

mongo-up:
	@if command -v brew >/dev/null 2>&1; then \
	  brew services list | grep -q "mongodb-community.*started" \
	    || brew services start mongodb-community; \
	else \
	  echo "Non-macOS: ensure MongoDB is running on localhost:27017"; \
	fi

dev_env: $(STAMP)

clean:
	rm -rf $(VENV)

prod: all_tests github

github: FORCE
	- git commit -a
	git push origin master

all_tests: FORCE
	$(MAKE) -C $(API_DIR) tests
	$(MAKE) -C $(COUNTRIES_DIR) tests
	$(MAKE) -C $(STATES_DIR) tests
	$(MAKE) -C $(CITIES_DIR) tests
	$(MAKE) -C $(SCORES_DIR) tests
	$(MAKE) -C $(USERS_DIR) tests
	$(MAKE) -C $(FRIENDS_DIR) tests
	$(MAKE) -C $(PROMPTS_DIR) tests

docs: FORCE
	$(MAKE) -C $(API_DIR) docs
