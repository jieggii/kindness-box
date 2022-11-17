DEBUG_ENV = debug.env

#date = $(shell date +"%d-%m-%Y-%H:%M:%S")

.PHONY: todo
todo:
	@echo "TODOs in the source code:"
	@grep -rn "todo" ./app/
	@echo
	@echo "TODOs in the todo.txt file:"
	@cat todo.txt

.PHONY: fmt
fmt:
	pdm run fmt

.PHONY: lint
lint:
	pdm run lint

.PHONY: debug
start-debug:
	pdm run dotenv -f $(DEBUG_ENV) run python -m app

.PHONY: docker-build
docker-build:
	docker build --tag kindness-box .

docker-run:
	docker run --network=host kindness-box:latest

backup-db:
	mkdir -p ./backup/
	pg_dump --user=kindness-box kindness-box > ./backup/$(shell date +%d.%m.%Y-%H:%M:%S).bak
