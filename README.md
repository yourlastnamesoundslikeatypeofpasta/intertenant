# intertenant

Simple Flask middleware that authenticates against two Acumatica tenants (`ruvira_group` and `ruvira_composites`) using the OpenAPI spec URLs in `assets/open_api_specs`.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Environment variables

Set credentials for both tenants:

- `ACUMATICA_SOURCE_USERNAME`
- `ACUMATICA_SOURCE_PASSWORD`
- `ACUMATICA_SOURCE_COMPANY`
- `ACUMATICA_SOURCE_BRANCH` (optional)
- `ACUMATICA_TARGET_USERNAME`
- `ACUMATICA_TARGET_PASSWORD`
- `ACUMATICA_TARGET_COMPANY`
- `ACUMATICA_TARGET_BRANCH` (optional)

## Run server

```bash
python app.py
```

### Endpoints

- `GET /health` - basic health check.
- `POST /auth/login` - performs login against both tenants and returns status for each.

## Tests

These tests intentionally perform **real HTTP logins** to the non-production Acumatica tenants.

```bash
pytest -m integration -v
```
