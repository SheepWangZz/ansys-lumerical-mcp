from __future__ import annotations

import os
import sys
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Any
from uuid import uuid4

from .errors import (
    LumericalApiCallError,
    LumericalImportError,
    LumericalSessionError,
    LumericalValidationError,
)


PRODUCT_CLASSES = {
    "fdtd": "FDTD",
    "mode": "MODE",
    "interconnect": "INTERCONNECT",
    "device": "DEVICE",
}

_SESSIONS: dict[str, dict[str, Any]] = {}
_EXECUTOR = ThreadPoolExecutor(max_workers=4, thread_name_prefix="lumerical-mcp")

LUMERICAL_INSTALL_ENV = "LUMERICAL_MCP_INSTALL_DIR"
LEGACY_LUMERICAL_INSTALL_ENV = "LUMERICAL_INSTALL_DIR"


def import_lumerical_core() -> tuple[Any | None, ImportError | None]:
    """Import ansys-lumerical-core lazily so status checks can explain failures."""
    try:
        _configure_lumerical_install_path()
        import ansys.lumerical.core as lumerical_core
    except ImportError as exc:
        return None, exc
    return lumerical_core, None


def package_version(package_name: str) -> str | None:
    try:
        return version(package_name)
    except PackageNotFoundError:
        return None


def get_lumerical_status() -> dict[str, Any]:
    module, error = import_lumerical_core()
    if error is not None:
        return {
            "available": False,
            "error": str(error),
            "products": list(PRODUCT_CLASSES),
            "package_version": package_version("ansys-lumerical-core"),
            "python_executable": sys.executable,
            "configured_lumerical_install_dir": _configured_lumerical_install_dir(),
        }

    interop_paths = module.InteropPaths
    return {
        "available": True,
        "module": getattr(module, "__name__", "ansys.lumerical.core"),
        "package_version": package_version("ansys-lumerical-core"),
        "api_version": getattr(module, "__version__", None),
        "products": list(PRODUCT_CLASSES),
        "python_executable": sys.executable,
        "configured_lumerical_install_dir": _configured_lumerical_install_dir(),
        "lumerical_install_dir": getattr(interop_paths, "LUMERICALINSTALLDIR", None),
        "interop_lib_dir": getattr(interop_paths, "INTEROPLIBDIR", None),
    }


def _configured_lumerical_install_dir() -> str | None:
    return os.environ.get(LUMERICAL_INSTALL_ENV) or os.environ.get(
        LEGACY_LUMERICAL_INSTALL_ENV
    )


def _configure_lumerical_install_path() -> None:
    install_dir = _configured_lumerical_install_dir()
    if not install_dir:
        return

    install_path = Path(install_dir)
    if not install_path.exists():
        raise ImportError(
            f"{LUMERICAL_INSTALL_ENV} points to a path that does not exist: "
            f"{install_dir}"
        )

    try:
        import ansys.api.lumerical.lumapi as raw_lumapi
    except ImportError as exc:
        raise ImportError(
            "Could not import ansys.api.lumerical.lumapi while configuring "
            "the Lumerical install path."
        ) from exc

    raw_lumapi.InteropPaths.setLumericalInstallPath(str(install_path))


def list_available_products() -> list[dict[str, str]]:
    return [
        {"name": product, "class": class_name}
        for product, class_name in PRODUCT_CLASSES.items()
    ]


def open_session(
    product: str,
    *,
    hide: bool = True,
    project: str | None = None,
    script: str | None = None,
    server_args: dict[str, Any] | None = None,
    remote_args: dict[str, Any] | None = None,
) -> dict[str, Any]:
    module = _require_lumerical_core()
    normalized, class_name = _product_class(product)
    session_class = getattr(module, class_name)

    kwargs: dict[str, Any] = {}
    if project:
        kwargs["project"] = _validated_existing_file(project, "project")
    if script:
        kwargs["script"] = _validated_existing_file(script, "script")

    try:
        session = session_class(
            hide=hide,
            serverArgs=server_args or {},
            remoteArgs=remote_args or {},
            **kwargs,
        )
    except Exception as exc:
        raise _api_call_error(
            f"Failed to open a Lumerical {normalized} session.",
            exc,
        ) from exc

    session_id = uuid4().hex
    _SESSIONS[session_id] = {
        "id": session_id,
        "product": normalized,
        "session": session,
        "hide": hide,
        "project": project,
        "script": script,
        "busy": False,
        "last_error": None,
    }

    return {
        "session_id": session_id,
        "product": normalized,
        "hide": hide,
        "project": project,
        "script": script,
    }


def list_sessions() -> list[dict[str, Any]]:
    return [
        {
            "session_id": session_id,
            "product": record["product"],
            "hide": record["hide"],
            "project": record["project"],
            "script": record["script"],
            "busy": record["busy"],
            "last_error": record["last_error"],
        }
        for session_id, record in _SESSIONS.items()
    ]


def close_session(session_id: str) -> dict[str, Any]:
    _validate_non_empty("session_id", session_id)
    record = _SESSIONS.pop(session_id, None)
    if record is None:
        raise LumericalSessionError(f"No active Lumerical session '{session_id}'.")
    if record["busy"]:
        _SESSIONS[session_id] = record
        raise LumericalSessionError(
            f"Lumerical session '{session_id}' is busy. Wait for the active call "
            "to finish before closing it."
        )

    try:
        record["session"].close()
    except Exception as exc:
        _SESSIONS[session_id] = record
        raise _api_call_error(
            f"Failed to close Lumerical session '{session_id}'.",
            exc,
        ) from exc

    return {"closed": True, "session_id": session_id, "product": record["product"]}


def run_script(
    session_id: str,
    code: str,
    timeout_seconds: float | None = None,
) -> dict[str, Any]:
    _validate_non_empty("code", code)
    session = _get_session(session_id)
    _run_with_optional_timeout(
        session_id,
        lambda: session.eval(code),
        timeout_seconds=timeout_seconds,
        failure_message=f"Failed to run script in Lumerical session '{session_id}'.",
    )

    return {"ok": True, "session_id": session_id}


def put_variable(session_id: str, name: str, value: Any) -> dict[str, Any]:
    _validate_variable_name(name)
    session = _get_session(session_id)
    try:
        session.putv(name, value)
    except Exception as exc:
        raise _api_call_error(
            f"Failed to set variable '{name}' in Lumerical session '{session_id}'.",
            exc,
        ) from exc

    return {"ok": True, "session_id": session_id, "name": name}


def get_variable(session_id: str, name: str) -> dict[str, Any]:
    _validate_variable_name(name)
    session = _get_session(session_id)
    try:
        value = session.getv(name)
    except Exception as exc:
        raise _api_call_error(
            f"Failed to read variable '{name}' from Lumerical session '{session_id}'.",
            exc,
        ) from exc

    return {"ok": True, "session_id": session_id, "name": name, "value": _json_safe(value)}


def _require_lumerical_core() -> Any:
    module, error = import_lumerical_core()
    if error is not None:
        raise LumericalImportError(str(error))
    return module


def _product_class(product: str) -> tuple[str, str]:
    _validate_non_empty("product", product)
    normalized = product.lower().strip()
    class_name = PRODUCT_CLASSES.get(normalized)
    if class_name is None:
        supported = ", ".join(PRODUCT_CLASSES)
        raise LumericalSessionError(
            f"Unsupported product '{product}'. Supported products: {supported}."
        )
    return normalized, class_name


def _get_session(session_id: str) -> Any:
    record = _get_session_record(session_id)
    if record["busy"]:
        raise LumericalSessionError(
            f"Lumerical session '{session_id}' is already running another call."
        )
    return record["session"]


def _get_session_record(session_id: str) -> dict[str, Any]:
    _validate_non_empty("session_id", session_id)
    record = _SESSIONS.get(session_id)
    if record is None:
        raise LumericalSessionError(f"No active Lumerical session '{session_id}'.")
    return record


def _run_with_optional_timeout(
    session_id: str,
    action: Any,
    *,
    timeout_seconds: float | None,
    failure_message: str,
) -> None:
    record = _get_session_record(session_id)
    if record["busy"]:
        raise LumericalSessionError(
            f"Lumerical session '{session_id}' is already running another call."
        )
    if timeout_seconds is not None and timeout_seconds <= 0:
        raise LumericalValidationError("timeout_seconds must be greater than 0.")

    record["busy"] = True
    record["last_error"] = None

    if timeout_seconds is None:
        try:
            action()
        except Exception as exc:
            record["last_error"] = str(exc)
            raise _api_call_error(failure_message, exc) from exc
        finally:
            record["busy"] = False
        return

    future = _EXECUTOR.submit(action)

    def _mark_complete(done_future: Any) -> None:
        record["busy"] = False
        try:
            done_future.result()
        except Exception as exc:
            record["last_error"] = str(exc)

    future.add_done_callback(_mark_complete)

    try:
        future.result(timeout=timeout_seconds)
    except TimeoutError as exc:
        raise LumericalApiCallError(
            f"{failure_message} Timed out after {timeout_seconds} seconds. "
            "The Lumerical call may still be running; this session will remain "
            "busy until the call finishes."
        ) from exc
    except Exception as exc:
        record["busy"] = False
        record["last_error"] = str(exc)
        raise _api_call_error(failure_message, exc) from exc
    else:
        record["busy"] = False


def _validated_existing_file(path: str, label: str) -> str:
    _validate_non_empty(label, path)
    file_path = Path(path).expanduser()
    if not file_path.exists():
        raise LumericalValidationError(f"{label} file does not exist: {path}")
    if not file_path.is_file():
        raise LumericalValidationError(f"{label} path is not a file: {path}")
    return str(file_path)


def _validate_non_empty(field: str, value: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise LumericalValidationError(f"{field} must be a non-empty string.")


def _validate_variable_name(name: str) -> None:
    _validate_non_empty("name", name)
    if any(char.isspace() for char in name):
        raise LumericalValidationError(
            "Variable name must not contain whitespace. "
            "Use a simple Lumerical workspace variable name."
        )


def _api_call_error(message: str, exc: Exception) -> LumericalApiCallError:
    detail = str(exc).strip() or exc.__class__.__name__
    return LumericalApiCallError(f"{message} Details: {detail}")


def _json_safe(value: Any) -> Any:
    try:
        import numpy as np
    except ImportError:
        np = None

    if value is None or isinstance(value, str | int | float | bool):
        return value
    if np is not None and isinstance(value, np.ndarray):
        return value.tolist()
    if np is not None and isinstance(value, np.generic):
        return value.item()
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, list | tuple):
        return [_json_safe(item) for item in value]
    return repr(value)
