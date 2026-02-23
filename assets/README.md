# Assets

This folder stores static project artifacts that support development and integration work.

## `open_api_specs/`

The JSON files in `assets/open_api_specs/` are Acumatica OpenAPI specification snapshots for the source and target tenants (including manufacturing variants).

These specs are kept in-repo to:

- document the exact endpoint and field contracts the middleware should map against;
- provide a stable, versioned reference when implementing or reviewing mapper/client changes;
- reduce accidental schema drift by giving developers a local source of truth without depending on live tenant access.

When adding or updating entity mappings, check these files first and align payload shapes (including Acumatica `{"value": ...}` wrappers) to the documented contracts.
