include common.mk

# Our directories
API_DIR = server
DB_DIR = data
SEC_DIR = security
STATES_DIR = states
COUNTIES_DIR = counties
COUNTRIES_DIR = countries
CITIES_DIR = cities
REQ_DIR = .

FORCE:

prod: all_tests github

github: FORCE
	- git commit -a
	git push origin master

all_tests: FORCE
	$(MAKE) -C $(API_DIR) tests
	$(MAKE) -C $(STATES_DIR) tests
	$(MAKE) -C $(COUNTIES_DIR) tests
	$(MAKE) -C $(COUNTRIES_DIR) tests
	$(MAKE) -C $(CITIES_DIR) tests

dev_env: FORCE
	pip install -r $(REQ_DIR)/requirements-dev.txt
	@echo "You should set PYTHONPATH to: "
	@echo $(shell pwd)

docs: FORCE
	$(MAKE) -C $(API_DIR) docs

# --- Local development targets ---

seed: FORCE
	PYTHONPATH=$(shell pwd):$$PYTHONPATH python -m scripts.load_script

start: FORCE
	./local.sh
