from __future__ import annotations

from typing import Any

from . import lumerical


def lumerical_status() -> dict[str, Any]:
    """Return package and local installation status without launching Lumerical."""
    return lumerical.get_lumerical_status()


def list_available_products() -> list[dict[str, str]]:
    """List supported Lumerical product sessions without launching them."""
    return lumerical.list_available_products()


def open_session(
    product: str,
    hide: bool = True,
    project: str | None = None,
    script: str | None = None,
    server_args: dict[str, Any] | None = None,
    remote_args: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Open a Lumerical session and return its session id."""
    return lumerical.open_session(
        product,
        hide=hide,
        project=project,
        script=script,
        server_args=server_args,
        remote_args=remote_args,
    )


def list_sessions() -> list[dict[str, Any]]:
    """List active sessions managed by this MCP server process."""
    return lumerical.list_sessions()


def close_session(session_id: str) -> dict[str, Any]:
    """Close an active Lumerical session."""
    return lumerical.close_session(session_id)


def run_script(
    session_id: str,
    code: str,
    timeout_seconds: float | None = None,
) -> dict[str, Any]:
    """Run Lumerical script code in an active session."""
    return lumerical.run_script(session_id, code, timeout_seconds=timeout_seconds)


def put_variable(session_id: str, name: str, value: Any) -> dict[str, Any]:
    """Put a JSON-compatible value into a Lumerical script workspace variable."""
    return lumerical.put_variable(session_id, name, value)


def get_variable(session_id: str, name: str) -> dict[str, Any]:
    """Read a variable from the Lumerical script workspace."""
    return lumerical.get_variable(session_id, name)
