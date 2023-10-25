FROM python:3.11 as builder

WORKDIR /kindness-box-build

RUN pip install -U pip setuptools wheel
RUN pip install pdm

COPY pyproject.toml pdm.lock* ./
#COPY bot/ ./bot

RUN mkdir __pypackages__ && pdm sync -v --prod --no-editable

FROM python:3.11

WORKDIR /kindness-box

COPY --from=builder /kindness-box-build/__pypackages__/3.11/bin/* /bin/
COPY --from=builder /kindness-box-build/__pypackages__/3.11/lib ./pkgs
COPY bot ./bot

ENV PYTHONPATH=/kindness-box/pkgs
ENTRYPOINT ["python", "-m", "bot"]
