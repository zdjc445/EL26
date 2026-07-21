ARG DOCKERHUB_REGISTRY=docker.io
FROM ${DOCKERHUB_REGISTRY}/library/python:3.13.14-alpine3.24@sha256:399babc8b49529dabfd9c922f2b5eea81d611e4512e3ed250d75bd2e7683f4b0 AS builder

ENV UV_PROJECT_ENVIRONMENT=/opt/venv \
    UV_LINK_MODE=copy
WORKDIR /workspace
RUN python -m pip install --no-cache-dir uv==0.11.29
COPY backend/pyproject.toml backend/uv.lock ./backend/
RUN uv sync --project backend --frozen --no-dev --no-install-project
COPY backend/src ./backend/src
RUN uv sync --project backend --frozen --no-dev --no-editable

FROM ${DOCKERHUB_REGISTRY}/library/python:3.13.14-alpine3.24@sha256:399babc8b49529dabfd9c922f2b5eea81d611e4512e3ed250d75bd2e7683f4b0 AS runtime
ENV PATH=/opt/venv/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    TIME_ENVIRONMENT=production
WORKDIR /app
COPY --from=builder /opt/venv /opt/venv
USER 10001:10001
EXPOSE 8000
CMD ["uvicorn", "time_agent.main:app", "--host", "0.0.0.0", "--port", "8000", "--no-access-log"]
