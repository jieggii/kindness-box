date = $(shell date +"%d-%m-%Y-%H:%M:%S")

fmt:
	poetry run isort app/
	poetry run black app/

lint:
	poetry run flake8 app/

run-local:
	poetry run dotenv -f .env run python -m app

docker-run:
	docker run -d --network=host giving-tuesday-bot:latest

docker-build:
	docker build --tag giving-tuesday-bot .

backup-db:
	mkdir -p ./backup/
	pg_dump --user=bot bot > ./backup/$(date).bak



