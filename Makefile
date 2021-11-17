fmt:
	poetry run isort app/
	poetry run black app/

lint:
	poetry run flake8 app/

run-debug:
	poetry run dotenv -f .env run python -m app

docker-run:
	docker run --network=host giving-tuesday-bot:latest

docker-build:
	docker build --tag giving-tuesday-bot .

test-db:
	poetry run dotenv -f .env run python test_db.py


