
VENV:=$(CURDIR)/build
PYTHON:=$(VENV)/bin/python3

test:PATH+=:$(VENV)/bin
test:
	# @echo ====== Show help
	# @troer --help
	@echo ====== Test lib
	@troer tests/test-lib.yaml -Itests
	# @echo ====== Test storage
	# @troer tests/test-storage.yaml -Itests
	# @echo ====== Test exchange
	# @troer tests/test-exchange.yaml -Itests

install:
	@python3 -m venv $(VENV)
	@$(PYTHON) -m pip install -e .

uninstall:
	@$(PYTHON) -m pip uninstall troer --yes

clobber:
	@rm -rf $(VENV)

.PHONY: test install uninstall clobber
