DEBUG_ENV = debug.env

#date = $(shell date +"%d-%m-%Y-%H:%M:%S")

.PHONY: todo
todo:
	grep -rn "todo" ./app/

.PHONY: fmt
fmt:
	pdm run fmt

.PHONY: lint
lint:
	pdm run lint

.PHONY: debug
start-debug:
	pdm run dotenv -f $(DEBUG_ENV) run python -m app

#docker-run:
#	docker run -d --network=host giving-tuesday-bot:latest
#
#docker-build:
#	docker build --tag giving-tuesday-bot .
#
#backup-db:
#	mkdir -p ./backup/
#	pg_dump --user=bot bot > ./backup/$(date).bak
