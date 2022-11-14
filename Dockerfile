FROM python:3.10

WORKDIR /kindness-box/

RUN pip install pdm==2.2.1
RUN pdm config check_update false && pdm config python.use_venv false

COPY pyproject.toml pdm.lock* .env  ./
COPY app app/

RUN pdm install --prod

ENTRYPOINT ["pdm", "run", "dotenv", "-f", ".env", "run", "python", "-m", "app"]