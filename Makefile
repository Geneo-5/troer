
.PHONY: test
test:PATH+=:$(HOME)/.local/bin
test:
	# @echo ====== Show help
	# @troer --help
	@echo ====== Test storage
	@troer --spec tests/test-storage.yaml --mode lib-header
	@troer --spec tests/test-storage.yaml --mode lib-src
	# @echo ====== Test exchange
	# @troer --spec tests/test-exchange.yaml --mode lib-header

install:
	@python3 -m pip install -e .

uninstall:
	@python3 -m pip uninstall troer --yes

