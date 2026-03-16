# Intertenant Authentication Checker

This repository contains a small Python utility (`app.py`) that validates login/logout authentication against two Acumatica tenants by reading each tenant's OpenAPI spec and using the first `servers[0].url` entry.

## What it does

- Loads tenant API base URLs from:
  - `assets/open_api_specs/ruvira_group_open_api.json`
  - `assets/open_api_specs/ruvira_composites_open_api_spec.json`
- Builds:
  - `.../entity/auth/login`
  - `.../entity/auth/logout`
- Attempts login + logout for each tenant using credentials from environment variables.
- Prints an authentication summary and exits with:
  - `0` when all checks succeed
  - `1` when any check fails or required environment variables are missing

## Requirements

- Python 3.10+
- Install dependencies:

```bash
pip install -r requirements.txt
```

## Environment variables

Set the following before running:

### Source tenant (`ruvira_group`)

- `ACUMATICA_SOURCE_USERNAME`
- `ACUMATICA_SOURCE_PASSWORD`
- `ACUMATICA_SOURCE_COMPANY`
- `ACUMATICA_SOURCE_BRANCH` (optional; empty is allowed)

### Target tenant (`ruvira_composites`)

- `ACUMATICA_TARGET_USERNAME`
- `ACUMATICA_TARGET_PASSWORD`
- `ACUMATICA_TARGET_COMPANY`
- `ACUMATICA_TARGET_BRANCH` (optional; empty is allowed)

## Run

```bash
python app.py
```

## Notes

- The script requires `USERNAME`, `PASSWORD`, and `COMPANY` variables for both tenants.
- The branch value is included in the login payload and may be left empty if not needed by the tenant.
- If an HTTP error occurs, the script prints status code and a truncated response body (up to 300 characters).
