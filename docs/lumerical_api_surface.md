# Lumerical API Surface

This project targets `ansys-lumerical-core==0.2.0`, imported as:

```python
import ansys.lumerical.core as lumapi
```

## Local Environment

- Python: `3.11.15`
- MCP SDK: `mcp==1.27.0`
- Lumerical package: `ansys-lumerical-core==0.2.0`
- Lumerical install path: discovered automatically or supplied through
  `LUMERICAL_MCP_INSTALL_DIR`

## Public Classes

The package exposes these product session classes:

- `lumapi.FDTD`
- `lumapi.MODE`
- `lumapi.INTERCONNECT`
- `lumapi.DEVICE`

All four share the same constructor shape:

```python
session = lumapi.FDTD(
    filename=None,
    key=None,
    hide=False,
    serverArgs={},
    remoteArgs={},
    **kwargs,
)
```

Useful keyword arguments from the upstream class docs include:

- `project`: open a Lumerical project file.
- `script`: run one script file or a list of script files after opening a project or blank session.
- `hide`: start with the GUI hidden.
- `serverArgs`: pass launch arguments to the local product executable.
- `remoteArgs`: connect to a remote interop server.

## Core Session Methods

Every product session inherits from `Lumerical` and supports:

- `eval(code: str)`: run Lumerical script code in the active session.
- `putv(varname: str, value)`: put a Python value into the Lumerical script workspace.
- `getv(varname: str)`: read a variable from the Lumerical script workspace.
- `close()`: close the product session.
- `getObjectById(id)`
- `getObjectBySelection()`
- `getAllSelectedObjects()`

Product-specific script commands are exposed dynamically after a session starts. For example, Lumerical script commands can be called as Python methods when available on the active product session.

## First MCP Tool Targets

Good first tools for the MCP server:

- `lumerical_status`: report import status, package version, discovered install path, interop path, and available product classes. Implemented.
- `list_available_products`: list supported product classes without launching a session. Implemented.
- `open_session`: create one session for `fdtd`, `mode`, `interconnect`, or `device`. Implemented.
- `list_sessions`: list sessions managed by the server process. Implemented.
- `close_session`: close an active session. Implemented.
- `run_script`: call `session.eval(...)` on an active session. Implemented.
- `put_variable`: call `session.putv(...)`. Implemented.
- `get_variable`: call `session.getv(...)`, converting NumPy arrays and simple structs into JSON-friendly values. Implemented.

## MCP Server Shape

The server uses Python and `mcp.server.fastmcp.FastMCP`.

- Transport: `stdio`
- Package entry point: `ansys_lumerical_mcp.server:main`
- Module entry point: `python -m ansys_lumerical_mcp`
- Direct Lumerical API calls stay in `lumerical.py`
- MCP tool registration stays in `server.py`
- Tool implementation helpers stay in `tools.py`

## Design Notes

- Keep direct calls to `ansys.lumerical.core` inside `lumerical.py`.
- Keep MCP tool declarations inside `server.py` or `tools.py`.
- Avoid launching sessions during import or status checks.
- Default session launches should use `hide=True` so tool calls do not pop up UI unless explicitly requested.
- Errors from Lumerical API calls are caught and converted into user-readable `LumericalApiCallError` messages.
- User inputs are validated before session calls. Empty session ids, empty script code, unknown products, missing project/script files, and whitespace in variable names are rejected before calling Lumerical.
- `run_script` accepts optional `timeout_seconds`. If the timeout expires, the MCP call returns an error and the session remains marked as busy until the underlying Lumerical call completes.
