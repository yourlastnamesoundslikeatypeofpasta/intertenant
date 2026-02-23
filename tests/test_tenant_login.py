import os

import pytest

from app import TENANTS, create_app, login_to_tenant


def _require_env(var_name: str) -> str:
    value = os.getenv(var_name)
    assert value, f"Required env var not set: {var_name}"
    return value


@pytest.mark.integration
@pytest.mark.parametrize("tenant_alias", ["source", "target"])
def test_login_to_each_tenant(tenant_alias: str) -> None:
    config = TENANTS[tenant_alias]

    # Hard assert that credentials are provided so this test always performs a real login.
    _require_env(config.username_env)
    _require_env(config.password_env)
    _require_env(config.company_env)

    result = login_to_tenant(config, timeout=45)

    assert result["ok"] is True
    assert result["status_code"] == 200
    assert result["login_url"].endswith("/entity/auth/login")


@pytest.mark.integration
def test_flask_endpoint_logs_into_both_tenants() -> None:
    for cfg in TENANTS.values():
        _require_env(cfg.username_env)
        _require_env(cfg.password_env)
        _require_env(cfg.company_env)

    app = create_app()
    client = app.test_client()

    response = client.post("/auth/login")

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["ok"] is True
    assert payload["tenants"]["source"]["ok"] is True
    assert payload["tenants"]["target"]["ok"] is True
