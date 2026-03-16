import json
import os
import sys
from pathlib import Path
from urllib.parse import urlsplit

import requests

ASSETS_DIR = Path(__file__).parent / "assets" / "open_api_specs"
TENANTS = {
    "source": {
        "tenant": "ruvira_group",
        "spec_file": "ruvira_group_open_api.json",
        "username_env": "ACUMATICA_SOURCE_USERNAME",
        "password_env": "ACUMATICA_SOURCE_PASSWORD",
        "company_env": "ACUMATICA_SOURCE_COMPANY",
        "branch_env": "ACUMATICA_SOURCE_BRANCH",
    },
    "target": {
        "tenant": "ruvira_composites",
        "spec_file": "ruvira_composites_open_api_spec.json",
        "username_env": "ACUMATICA_TARGET_USERNAME",
        "password_env": "ACUMATICA_TARGET_PASSWORD",
        "company_env": "ACUMATICA_TARGET_COMPANY",
        "branch_env": "ACUMATICA_TARGET_BRANCH",
    },
}


def run_authentication(timeout: float = 30.0) -> int:
    results = {}
    overall_ok = True

    for alias, tenant in TENANTS.items():
        try:
            with (ASSETS_DIR / tenant["spec_file"]).open("r", encoding="utf-8") as handle:
                data = json.load(handle)

            servers = data.get("servers") or []
            if not servers or "url" not in servers[0]:
                raise ValueError(f"Unable to determine server URL from spec {tenant['spec_file']}")

            parsed = urlsplit(str(servers[0]["url"]))
            root = f"{parsed.scheme}://{parsed.netloc}{parsed.path.split('/entity/')[0].rstrip('/')}"
            login_url = f"{root}/entity/auth/login"
            logout_url = f"{root}/entity/auth/logout"

            credentials = {
                "name": os.getenv(tenant["username_env"], ""),
                "password": os.getenv(tenant["password_env"], ""),
                "company": os.getenv(tenant["company_env"], ""),
                "branch": os.getenv(tenant["branch_env"], ""),
            }
            missing = [field for field in ("name", "password", "company") if not credentials[field]]
            if missing:
                raise ValueError(f"Missing credentials ({', '.join(missing)})")

            with requests.Session() as session:
                response = session.post(login_url, json=credentials, timeout=timeout)
                response.raise_for_status()
                session.post(logout_url, timeout=timeout)

            results[alias] = f"ok ({response.status_code})"
        except Exception as exc:
            overall_ok = False
            results[alias] = f"failed: {exc}"

    print("Authentication summary:")
    for alias, result in results.items():
        print(f"- {alias}: {result}")

    return 0 if overall_ok else 1


if __name__ == "__main__":
    sys.exit(run_authentication())
