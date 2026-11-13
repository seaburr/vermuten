ifndef VERMUTEN_CONFIG
override VERMUTEN_CONFIG = demo.json
endif

test:
	export VERMUTEN_CONFIG=demo.json && python3 -m unittest discover tests "test_vermuten.py"

run: test
	export VERMUTEN_CONFIG=$(VERMUTEN_CONFIG) && gunicorn app:app

win-run: test
	set VERMUTEN_CONFIG=$(VERMUTEN_CONFIG) && waitress-serve --listen="127.0.0.1:5000" app:app

apply-formatting:
	black ./

lint:
	pip3 install black
	python3 -m black --check ./
