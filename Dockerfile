ARG BASE_IMAGE=nn-docker.artifactory.insim.biz/library/python:3.12-slim
FROM ${BASE_IMAGE}

ARG PIP_INDEX_URL
ARG PIP_EXTRA_INDEX_URL

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY pyproject.toml README.md ./
COPY app ./app

RUN pip install --no-cache-dir --upgrade pip \
    && if [ -n "$PIP_INDEX_URL" ] && [ -n "$PIP_EXTRA_INDEX_URL" ]; then \
        pip install --no-cache-dir --index-url "$PIP_INDEX_URL" --extra-index-url "$PIP_EXTRA_INDEX_URL" .; \
    elif [ -n "$PIP_INDEX_URL" ]; then \
        pip install --no-cache-dir --index-url "$PIP_INDEX_URL" .; \
    else \
        pip install --no-cache-dir .; \
    fi

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
