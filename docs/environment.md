# Environment And Paths

The distributed MCP server should run through the installed console command:

```text
ansys-lumerical-mcp
```

For local development, install the package into your active Python environment:

```powershell
python -m pip install -e ".[tests]"
python -m ansys_lumerical_mcp
```

The server uses `ansys-lumerical-core` as its Python dependency. That package
can auto-discover many local Lumerical installations.

If auto-discovery fails, set this environment variable:

```text
LUMERICAL_MCP_INSTALL_DIR=<path-to-lumerical-install>
```

`LUMERICAL_INSTALL_DIR` is also accepted as a fallback for compatibility, but
`LUMERICAL_MCP_INSTALL_DIR` is preferred because it is specific to this server.

Example MCP client configuration:

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

For client-specific notes and verification commands, see
`docs/mcp_client_configuration.md`.
