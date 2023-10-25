DEBUG_ENV = debug.env
PROD_ENV = .env

#.PHONY: todo
#todo:
#	@echo "TODOs in the source code:"
#	@grep -rn "todo" ./app/ ./scripts/
#	@echo
#	@echo "TODOs in the todo.txt file:"
#	@cat todo.txt

#.PHONY: debug
#start-debug:
#	pdm run dotenv -f $(DEBUG_ENV) run python -m app

#.PHONY: docker-build
#docker-build:
#	docker build --tag kindness-box .

#.PHONY: docker-run
#docker-run:
#	docker run -d --network=host kindness-box:latest

#.PHONY: init-db
#init-db:
#	pdm run python scripts/init-db.py --exec scripts/init-db.sql --env $(PROD_ENV) persons.xlsx

#.PHONY: add-person
#add-person:
#	pdm run python scripts/add-person.py --env $(PROD_ENV)

#.PHONY: backup-db
#backup-db:
#	mkdir -p backup
#	pg_dump --user=kindness-box kindness-box > ./backup/$(shell date +%d.%m.%Y-%H:%M:%S).bak
