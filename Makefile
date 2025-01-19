
VENV:=$(CURDIR)/build
PYTHON:=$(VENV)/bin/python3

test:PATH+=:$(VENV)/bin
test:
	# @echo ====== Show help
	# @troer --help
	@echo ====== Test storage
	@troer --spec tests/test-storage.yaml --all
	# @echo ====== Test exchange
	# @troer --spec tests/test-exchange.yaml --mode lib-header

install:
	@python3 -m venv $(VENV)
	@$(PYTHON) -m pip install -e .

uninstall:
	@$(PYTHON) -m pip uninstall troer --yes

clobber:
	@rm -rf $(VENV)

.PHONY: test install uninstall clobber
