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
	cd $(API_DIR); make tests
	cd $(STATES_DIR); make tests
	cd $(COUNTIES_DIR); make tests
	cd $(COUNTRIES_DIR); make tests
	cd $(CITIES_DIR); make tests
	# cd $(DB_DIR); make tests

dev_env: FORCE
	pip install -r $(REQ_DIR)/requirements-dev.txt
	@echo "You should set PYTHONPATH to: "
	@echo $(shell pwd)

docs: FORCE
	cd $(API_DIR); make docs

# --- Local development targets ---

seed: FORCE
	PYTHONPATH=$(shell pwd):$$PYTHONPATH python -m scripts.load_script

start: FORCE
	./local.sh
