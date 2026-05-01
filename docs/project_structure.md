# Project Structure

```text
ansys-lumerical-mcp/
|-- docs/
|   |-- environment.md
|   |-- local_testing.md
|   |-- lumerical_api_surface.md
|   |-- mcp_client_configuration.md
|   `-- project_structure.md
|-- examples/
|   `-- client_config.json
|-- src/
|   `-- ansys_lumerical_mcp/
|       |-- __init__.py
|       |-- __main__.py
|       |-- errors.py
|       |-- lumerical.py
|       |-- server.py
|       `-- tools.py
|-- tests/
|   |-- test_import.py
|   `-- test_server.py
|-- .gitignore
|-- LICENSE
|-- pyproject.toml
`-- README.md
```

## Purpose

- `src/ansys_lumerical_mcp`: installable Python package.
- `server.py`: MCP server creation and stdio startup.
- `tools.py`: MCP tool implementation functions.
- `lumerical.py`: direct `ansys-lumerical-core` integration.
- `tests`: automated checks for imports, server creation, and future tool behavior.
- `examples`: MCP client configuration snippets.
- `docs`: design notes and implementation decisions.
