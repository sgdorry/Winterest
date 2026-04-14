# common make vars and targets:
export LINTER = flake8
export PYLINTFLAGS = --exclude=__main__.py

export CLOUD_MONGO = 0

PYTHONFILES := $(wildcard *.py)
PYTESTFLAGS = -vv --verbose --cov-branch --cov-report term-missing --tb=short -W ignore::FutureWarning

MAIL_METHOD = api

FORCE:

tests: lint pytests

lint: $(patsubst %.py,%.pylint,$(PYTHONFILES))

%.pylint:
	$(LINTER) $(PYLINTFLAGS) $*.py

ifeq ($(OS),Windows_NT)
    PYPATH := $(shell cd .. && cd)
    SET_PYTHONPATH = set PYTHONPATH=$(PYPATH) &&
else
    PYPATH := $(shell cd .. && pwd)
    SET_PYTHONPATH = PYTHONPATH=$(PYPATH)
endif

pytests: FORCE
	$(SET_PYTHONPATH) pytest $(PYTESTFLAGS) --cov=$(PKG)

# test a python file:
%.py: FORCE
	$(LINTER) $(PYLINTFLAGS) $@
	pytest $(PYTESTFLAGS) tests/test_$*.py

nocrud:
	-rm *~
	-rm *.log
	-rm *.out
	-rm .*swp
	-rm $(TESTDIR)/*~
