from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

import requests
from flask import Flask, jsonify

ASSETS_DIR = Path(__file__).parent / "assets" / "open_api_specs"


@dataclass(frozen=True)
class TenantConfig:
    key: str
    spec_file: str
    username_env: str
    password_env: str
    company_env: str
    branch_env: str


TENANTS: dict[str, TenantConfig] = {
    "source": TenantConfig(
        key="ruvira_group",
        spec_file="ruvira_group_open_api.json",
        username_env="ACUMATICA_SOURCE_USERNAME",
        password_env="ACUMATICA_SOURCE_PASSWORD",
        company_env="ACUMATICA_SOURCE_COMPANY",
        branch_env="ACUMATICA_SOURCE_BRANCH",
    ),
    "target": TenantConfig(
        key="ruvira_composites",
        spec_file="ruvira_composites_open_api_spec.json",
        username_env="ACUMATICA_TARGET_USERNAME",
        password_env="ACUMATICA_TARGET_PASSWORD",
        company_env="ACUMATICA_TARGET_COMPANY",
        branch_env="ACUMATICA_TARGET_BRANCH",
    ),
}


def _load_server_url(spec_file: str) -> str:
    with (ASSETS_DIR / spec_file).open("r", encoding="utf-8") as handle:
        data = json.load(handle)

    servers = data.get("servers") or []
    if not servers or "url" not in servers[0]:
        raise ValueError(f"Unable to determine server URL from spec {spec_file}")

    return str(servers[0]["url"])


def _acumatica_instance_root(server_url: str) -> str:
    parsed = urlsplit(server_url)
    # strip OpenAPI path and keep the Acumatica instance root
    base_path = parsed.path.split("/entity/")[0].rstrip("/")
    return f"{parsed.scheme}://{parsed.netloc}{base_path}"


def _credentials(config: TenantConfig) -> dict[str, Any]:
    return {
        "name": os.getenv(config.username_env, ""),
        "password": os.getenv(config.password_env, ""),
        "company": os.getenv(config.company_env, ""),
        "branch": os.getenv(config.branch_env, ""),
    }


def _validate_creds(credentials: dict[str, Any], tenant: str) -> None:
    missing = [k for k in ("name", "password", "company") if not credentials.get(k)]
    if missing:
        fields = ", ".join(missing)
        raise ValueError(f"Missing required credential fields for tenant '{tenant}': {fields}")


def login_to_tenant(config: TenantConfig, timeout: float = 30.0) -> dict[str, Any]:
    credentials = _credentials(config)
    _validate_creds(credentials, config.key)

    server_url = _load_server_url(config.spec_file)
    root = _acumatica_instance_root(server_url)
    login_url = f"{root}/entity/auth/login"
    logout_url = f"{root}/entity/auth/logout"

    with requests.Session() as session:
        response = session.post(login_url, json=credentials, timeout=timeout)
        response.raise_for_status()
        session.post(logout_url, timeout=timeout)

    return {
        "tenant": config.key,
        "login_url": login_url,
        "status_code": response.status_code,
        "ok": True,
    }


def create_app() -> Flask:
    app = Flask(__name__)

    @app.get("/health")
    def health() -> Any:
        return jsonify({"status": "ok"})

    @app.post("/auth/login")
    def login_both() -> Any:
        results = {}
        overall_ok = True

        for alias, config in TENANTS.items():
            try:
                results[alias] = login_to_tenant(config)
            except Exception as exc:  # pragma: no cover - error surface for API callers
                overall_ok = False
                results[alias] = {
                    "tenant": config.key,
                    "ok": False,
                    "error": str(exc),
                }

        status_code = 200 if overall_ok else 502
        return jsonify({"ok": overall_ok, "tenants": results}), status_code

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")))
