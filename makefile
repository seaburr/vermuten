ifndef VERMUTEN_CONFIG
override VERMUTEN_CONFIG = demo.json
endif

default: help

help:
	@echo run: Runs tests and starts Gunicorn (NOT supported on Windows.)
	@echo win-run: Runs tests and starts Waiter.
	@echo test: Runs unit tests.
	@echo apply-formatting: Runs Black and ensures code is conformant with PEP."
test:
	python3 -m unittest discover tests "*_tests.py"

run: test
	VERMUTEN_CONFIG=$(VERMUTEN_CONFIG) && gunicorn app:app

win-run: test
	set VERMUTEN_CONFIG=$(VERMUTEN_CONFIG) && waitress-serve --listen="127.0.0.1:5000" app:app

apply-formatting:
	black ./