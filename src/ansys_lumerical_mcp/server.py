from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from . import tools


SERVER_NAME = "ansys-lumerical-mcp"


def create_server() -> FastMCP:
    server = FastMCP(
        SERVER_NAME,
        instructions=(
            "MCP server for Ansys Lumerical automation. "
            "Use status and product-listing tools before opening solver sessions."
        ),
    )

    server.tool(
        name="lumerical_status",
        description=(
            "Report ansys-lumerical-core availability, package version, "
            "discovered Lumerical installation path, and supported products. "
            "This does not launch a Lumerical session."
        ),
    )(tools.lumerical_status)
    server.tool(
        name="list_available_products",
        description=(
            "List the supported Lumerical product session types without "
            "launching Lumerical."
        ),
    )(tools.list_available_products)
    server.tool(
        name="open_session",
        description=(
            "Open a Lumerical session for fdtd, mode, interconnect, or device. "
            "This may launch Lumerical and consume a license."
        ),
    )(tools.open_session)
    server.tool(
        name="list_sessions",
        description="List Lumerical sessions opened by this MCP server process.",
    )(tools.list_sessions)
    server.tool(
        name="close_session",
        description="Close an active Lumerical session by session id.",
    )(tools.close_session)
    server.tool(
        name="run_script",
        description=(
            "Run Lumerical script code in an active session. Optionally pass "
            "timeout_seconds to stop waiting for very long calls."
        ),
    )(tools.run_script)
    server.tool(
        name="put_variable",
        description="Set a variable in an active Lumerical script workspace.",
    )(tools.put_variable)
    server.tool(
        name="get_variable",
        description="Read a variable from an active Lumerical script workspace.",
    )(tools.get_variable)

    return server


def main() -> None:
    create_server().run(transport="stdio")
