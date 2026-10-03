ARG PYTHON_VERSION=3.12

# Builder (install build deps & Poetry)
FROM python:-slim AS builder
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential libpq-dev && \
    rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY pyproject.toml poetry.lock ./
RUN pip install --no-cache-dir poetry==1.7.1
RUN poetry config virtualenvs.create false && \n    poetry install --only=main --no-interaction --no-ansi

# Final runtime image
FROM python:-slim
RUN apt-get update && \
    apt-get install -y --no-install-recommends libpq5 && \
    rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY --from=builder /usr/local/lib/python/site-packages \
    /usr/local/lib/python/site-packages
COPY --from=builder /usr/local/bin/poetry /usr/local/bin/poetry
COPY . .
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
CMD [ python, -m, dorama_studio.scripts.run_pipeline]
