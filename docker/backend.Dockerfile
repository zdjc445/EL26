ARG DOCKERHUB_REGISTRY=docker.io
FROM ${DOCKERHUB_REGISTRY}/library/python:3.13.14-slim-bookworm@sha256:9d7f287598e1a5a978c015ee176d8216435aaf335ed69ac3c38dd1bbb10e8d64 AS builder

ENV UV_PROJECT_ENVIRONMENT=/opt/venv \
    UV_LINK_MODE=copy
WORKDIR /workspace
RUN python -m pip install --no-cache-dir uv==0.11.29
COPY backend/pyproject.toml backend/uv.lock ./backend/
RUN uv sync --project backend --frozen --no-dev --no-install-project
COPY backend/src ./backend/src
RUN uv sync --project backend --frozen --no-dev --no-editable

FROM ${DOCKERHUB_REGISTRY}/library/python:3.13.14-slim-bookworm@sha256:9d7f287598e1a5a978c015ee176d8216435aaf335ed69ac3c38dd1bbb10e8d64 AS runtime
ENV PATH=/opt/venv/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    TIME_ENVIRONMENT=production
WORKDIR /app
COPY --from=builder /opt/venv /opt/venv
USER 10001:10001
EXPOSE 8000
CMD ["uvicorn", "time_agent.main:app", "--host", "0.0.0.0", "--port", "8000", "--no-access-log"]
