# MCP Client Configuration

Use stdio transport and launch the server with the installed console command.

## Installed Package Configuration

After installing the package, most clients can use:

```json
{
  "mcpServers": {
    "ansys-lumerical": {
      "command": "ansys-lumerical-mcp"
    }
  }
}
```

For Codex, add the server to your Codex `config.toml`:

```toml
[mcp_servers.ansys-lumerical]
command = "ansys-lumerical-mcp"
```

If `ansys-lumerical-core` cannot auto-discover Lumerical, add a local install
path in your own client configuration:

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

The same fallback in Codex TOML is:

```toml
[mcp_servers.ansys-lumerical]
command = "ansys-lumerical-mcp"
env = { LUMERICAL_MCP_INSTALL_DIR = "C:\\Path\\To\\Lumerical\\vXXX" }
```

## Local Development Configuration

For development from source, prefer an editable install instead of setting
`PYTHONPATH` in committed examples:

```powershell
python -m pip install -e ".[tests]"
python -m ansys_lumerical_mcp
```

## Verification

Run these checks from a shell where the package is installed:

```powershell
python -c "from ansys_lumerical_mcp.tools import lumerical_status; print(lumerical_status())"
```

Expected result:

```text
'available': True
```

To start the MCP server manually:

```powershell
ansys-lumerical-mcp
```

The process waits for MCP messages on stdin/stdout, so it may appear idle when
started manually. That is normal.
