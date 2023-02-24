SHELL=/bin/bash
.DEFAULT_GOAL := _help

# NOTE: must put a <TAB> character and two pound "\t##" to show up in this list.  Keep it brief! IGNORE_ME
.PHONY: _help
_help:
	@grep -h "##" $(MAKEFILE_LIST) | grep -v IGNORE_ME | sed -e 's/##//' | column -t -s $$'\t'



# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Initialize venv, install requirements
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# TODO: OS-independent venv, e.g. .venv/Scripts/activate

init:	## Initialize venv
	$(PY_SYS_INTERPRETER) -m venv .venv
	direnv allow || source .venv/bin/activate

PYTHON ?= $(shell which python)
PWD ?= $(shell pwd)
.PHONY: _venv
_venv:
	# ensuring venv
	[ "$(PYTHON)" = "$(PWD)/.venv/bin/python" ] || [ "$(PYTHON)" = "$(PWD)/.venv/Scripts/python" ]

deps: _venv	## Install requirements & sub-module
	git submodule update --init
	pip install -r requirements.txt
	- pip install -r requirements-lint.txt



# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Lint, test, format, clean
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

ALL_LINT_LOCS=pr *.py pong/ tests/

format: _venv	## Format the code
	isort $(ALL_LINT_LOCS)
	black $(ALL_LINT_LOCS)

lint: _venv	## Lint the code
	# check formatting: Python
	isort --diff --check $(ALL_LINT_LOCS)
	black --check $(ALL_LINT_LOCS)
	# lint Python
	pycodestyle $(ALL_LINT_LOCS)
	bandit -c .banditrc -q -r $(ALL_LINT_LOCS)
	flake8 --statistics --doctests $(ALL_LINT_LOCS)
	pylint $(ALL_LINT_LOCS)
	mypy $(ALL_LINT_LOCS)

test: _venv	## Test the code
	coverage run -m pytest tests/
	coverage report

ALL_CLEAN_LOCS=build/ *.egg-info
ALL_CLEAN_ARGS=-name .coverage -o -name __pycache__ -o -name .pytest_cache -o -name .mypy_cache
clean:	## Clean up pycache/ and other left overs
	rm -rf $(ALL_CLEAN_LOCS)
	rm -rf $(shell find . -maxdepth 1 $(ALL_CLEAN_ARGS))
	rm -rf $(shell find $(ALL_LINT_LOCS) $(ALL_CLEAN_ARGS))



# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Install, build
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

PY_SYS_INTERPRETER ?= /usr/bin/python3

install:	## Install into user space
	$(PY_SYS_INTERPRETER) -m pip install .

build: _venv	## Bundle a source distribution
	$(PYTHON) setup.py sdist



# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Rank
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

rank:	## Rank (copy for google sheet)
	./pr fetch
	./pr rank --no-abbrev-titles -s -mg | xclip -sel clip



# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Verify targets
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

N_ANNOTATED_FILES_ACTUAL ?= $(shell grep @author $(shell git ls-files \*.py) | wc -l)
N_ANNOTATED_FILES_EXPECT ?= $(shell git ls-files \*.py | grep -v glicko2 | wc -l)
verify/py-annotated:	## Verify all pythong files have the annotation at top
	[[ "$(N_ANNOTATED_FILES_ACTUAL)" == "$(N_ANNOTATED_FILES_EXPECT)" ]]
