# Birth Map Agent Demo

Minimal Python API agent to test runtime orchestration with multi-turn behavior and a deterministic stub result.

## What this demo proves

- Exposed API workflow suitable for platform runtime tests.
- Session-based state management across multiple requests.
- More than one LLM call in the flow (questioning + normalization) when credentials are set.
- Deterministic fallback behavior without LLM credentials.
- Containerized shipping flow.

## Requirements

- Python 3.12+
- `pip` (or `uv` if preferred)
- Docker (for containerized run)

## Local setup

1. Copy env template:

```bash
cp .env.example .env
```

2. LLM values are hard-coded for the POC in `app/config.py` (TENANT_ID, CLIENT_ID, CLIENT_SECRET, OPENAI_APP_API_ID, AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_DEPLOYMENT, AZURE_OPENAI_VERSION). Replace these values or move them to `.env` for production.

3. Create venv + install:

```bash
python3 -m venv .venv && .venv/bin/pip install --upgrade pip && .venv/bin/pip install -e .
```

## Run locally

```bash
.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Build and run as container

Build image:

```bash
docker build -t birth-map-agent-demo:latest .
```

Default base image is from Artifactory:

- `nn-docker.artifactory.insim.biz/library/python:3.12-slim`

If you need to override base image or force pip install through Artifactory with credentials:

```bash
docker build \
  --build-arg BASE_IMAGE=nn-docker.artifactory.insim.biz/library/python:3.12-slim \
  --build-arg PIP_INDEX_URL=https://<USER>:<TOKEN>@artifactory.insim.biz/artifactory/api/pypi/nn-pypi/simple \
  -t birth-map-agent-demo:latest .
```

Run container:

```bash
docker run --rm -p 8000:8000 --env-file .env birth-map-agent-demo:latest
```

## Endpoints

- `GET /health`
- `POST /sessions`
- `POST /sessions/{session_id}/input`
- `GET /sessions/{session_id}`

## Example flow

1. Create session:

```bash
curl -s -X POST http://localhost:8000/sessions
```

2. Submit fields in multiple turns (agent asks for missing values):

```bash
curl -s -X POST http://localhost:8000/sessions/<SESSION_ID>/input \
  -H "content-type: application/json" \
  -d '{"birthdate":"1990-01-15"}'
```

```bash
curl -s -X POST http://localhost:8000/sessions/<SESSION_ID>/input \
  -H "content-type: application/json" \
  -d '{"birth_time":"07:35","location":"Colombo, Sri Lanka"}'
```

3. Read final state:

```bash
curl -s http://localhost:8000/sessions/<SESSION_ID>
```

The output is a deterministic demo birth map (`kendaraya_type = demo-stub`) for the same inputs.
