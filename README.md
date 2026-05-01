# Ansys Lumerical MCP Server

MCP server for automating Ansys Lumerical through `ansys-lumerical-core`.

## Installation

Requires Python `>=3.10,<4`, matching the supported Python range declared by
`ansys-lumerical-core`.

With pip:

```powershell
python -m pip install ansys-lumerical-mcp
```

Pip reads this package metadata, checks the active Python version, and installs
the required runtime dependencies automatically:

- `ansys-lumerical-core>=0.2.0`
- `mcp>=1.27.0`

With conda:

```powershell
conda create -n ansys-lumerical-mcp python=3.13 pip
conda activate ansys-lumerical-mcp
python -m pip install ansys-lumerical-mcp
```

From a source checkout, conda users can also create an environment with:

```powershell
conda env create -f environment.yml
conda activate ansys-lumerical-mcp
```

That source environment installs this project in editable mode and lets pip
resolve the runtime dependencies.

## Development

```powershell
python -m pip install -e ".[tests]"
python -m ansys_lumerical_mcp
```

The server uses the MCP SDK's stdio transport. The first implemented tool is
`lumerical_status`, which checks the Python package and discovered local
Lumerical installation without launching a solver session.

Implemented tools:

- `lumerical_status`
- `list_available_products`
- `open_session`
- `list_sessions`
- `close_session`
- `run_script`
- `put_variable`
- `get_variable`

## Project layout

```text
ansys-lumerical-mcp/
├─ docs/
├─ examples/
├─ src/
│  └─ ansys_lumerical_mcp/
├─ tests/
├─ pyproject.toml
├─ README.md
├─ LICENSE
└─ .gitignore
```

## Build

```powershell
python -m pip install -e ".[build]"
python -m build
```

## MCP client configuration

The same configuration is also available at
`examples/client_config.json`. See `docs/mcp_client_configuration.md` for the
full setup notes, including Codex configuration and verification commands.

```json
{
  "mcpServers": {
    "ansys-lumerical": {
      "command": "ansys-lumerical-mcp",
      "env": {
        "LUMERICAL_MCP_INSTALL_DIR": "C:\\Path\\To\\Lumerical\\vXXX"
      }
    }
  }
}
```

`LUMERICAL_MCP_INSTALL_DIR` is optional when `ansys-lumerical-core`
auto-discovers the local installation. If discovery works, remove the `env`
block entirely. Keep machine-specific paths in your local MCP client settings,
not in committed project files.

For Codex, the installed-package configuration is:

```toml
[mcp_servers.ansys-lumerical]
command = "ansys-lumerical-mcp"
```
