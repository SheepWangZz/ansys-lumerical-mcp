# Local Testing

Test date: 2026-05-01

## Environment

- Python: `3.11`
- Package mode: source checkout with local development environment
- `LUMERICAL_MCP_INSTALL_DIR`: set locally when auto-discovery is not enough

## Results

- Python syntax compile for `src` and `tests`: passed.
- Direct server construction through `create_server()`: passed.
- `lumerical_status`: passed.
- `list_available_products`: passed.
- `list_sessions`: passed and returned an empty list before opening any session.
- MCP stdio client test: blocked by Windows sandbox pipe permissions before the server process started.
- Editable install with pip: blocked by local temp/build-tracker permissions.
- Hidden FDTD session launch: reached the Lumerical API but failed with `appOpen error: Failed to start messaging, check licenses...`.

## Interpretation

The MCP package code imports, compiles, and safe tools run in the target Python
environment. A real FDTD session cannot be opened until local Lumerical
messaging and license access are working.

The failed FDTD launch confirms the server's error wrapper is working:

```text
LumericalApiCallError: Failed to open a Lumerical fdtd session.
Details: appOpen error: Failed to start messaging, check licenses...
```
