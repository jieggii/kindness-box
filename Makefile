DEBUG_ENV = debug.env
#PROD_ENV = .env

.PHONY: todo
todo:
	@grep -rn "todo" ./app/ ./scripts/

.PHONY: debug
start-debug:
	pdm run dotenv -f $(DEBUG_ENV) run python -m app

#.PHONY: docker-build
#docker-build:
#	docker build --tag kindness-box .
#
#.PHONY: docker-run
#docker-run:
#	docker run -d --network=host kindness-box:latest

#.PHONY: backup-db
#backup-db:
#	mkdir -p backup
#	pg_dump --user=kindness-box kindness-box > ./backup/$(shell date +%d.%m.%Y-%H:%M:%S).bak
