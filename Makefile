SYSTEM_PYTHON = python3
VENV          = venv
PYTHON        = $(VENV)/bin/python3
FLAKE8        = $(VENV)/bin/flake8
MYPY          = $(VENV)/bin/mypy
MAIN_SCRIPT   = main.py
# make run MAP=maps/medium.txt
MAP ?= maps/default.txt

.PHONY: install run debug clean fclean re lint lint-strict

install:
	$(SYSTEM_PYTHON) -m venv $(VENV)
	$(VENV)/bin/pip install flake8 mypy

run:
	$(PYTHON) $(MAIN_SCRIPT) $(MAP)

debug:
	$(PYTHON) -m pdb $(MAIN_SCRIPT) $(MAP)

clean:
	rm -rf __pycache__
	rm -rf .mypy_cache

fclean: clean
	rm -rf $(VENV)

re: fclean install

lint:
	$(FLAKE8) --exclude=$(VENV) .
	$(MYPY) --exclude $(VENV) --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs .

lint-strict:
	$(FLAKE8) --exclude=$(VENV) .
	$(MYPY) --exclude $(VENV) --strict .