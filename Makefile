SHELL=/bin/bash
.DEFAULT_GOAL := _help

# NOTE: must put a <TAB> character and two pound "\t##" to show up in this list.  Keep it brief! IGNORE_ME
.PHONY: _help
_help:
	@grep -h "##" $(MAKEFILE_LIST) | grep -v IGNORE_ME | sed -e 's/##//' | column -t -s $$'\t'



# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Initialize & clean
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

init:
	git submodule update --init
	pip install -r requirements.txt -r requirements-lint.txt

clean:
	rm -rf .coverage __pycache__/ .pytest_cache/



# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Lint, test, format
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

ALL_LINT_LOCS=*.py pong/ tests/

format:	## Format the code
	isort $(ALL_LINT_LOCS)
	black $(ALL_LINT_LOCS)

lint:	## Lint the code
	# check formatting: Python
	isort --diff --check $(ALL_LINT_LOCS)
	black --check $(ALL_LINT_LOCS)
	# lint Python
	pycodestyle $(ALL_LINT_LOCS)
	bandit -c .banditrc -q -r $(ALL_LINT_LOCS)
	flake8 --statistics --doctests $(ALL_LINT_LOCS)
	pylint $(ALL_LINT_LOCS)
	# failing lints
	- mypy $(ALL_LINT_LOCS)

test:	## Test the code
	coverage run -m pytest tests/
	coverage report