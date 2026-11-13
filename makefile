ifndef VERMUTEN_CONFIG
override VERMUTEN_CONFIG = demo.json
endif

PORT ?= 8080

install:
	pip3 install -r requirements.txt -r requirements-dev.txt

test:
	python3 -m unittest

run: test
	VERMUTEN_CONFIG=$(VERMUTEN_CONFIG) gunicorn --bind 0.0.0.0:$(PORT) --workers 1 --threads 4 app:app

docker-build:
	docker build --platform linux/amd64 -t vermuten .

docker-run:
	docker run --rm -p $(PORT):8080 -e VERMUTEN_CONFIG=$(VERMUTEN_CONFIG) vermuten

apply-formatting:
	python3 -m black .

lint:
	python3 -m black --check .
