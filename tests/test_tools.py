import pytest

from ansys_lumerical_mcp.errors import LumericalSessionError, LumericalValidationError
from ansys_lumerical_mcp.lumerical import (
    LUMERICAL_INSTALL_ENV,
    _SESSIONS,
    _configured_lumerical_install_dir,
    _get_session,
    _json_safe,
    _product_class,
    _validate_variable_name,
    _validated_existing_file,
)
from ansys_lumerical_mcp.tools import list_available_products, list_sessions


def test_list_available_products():
    products = list_available_products()

    assert {"name": "fdtd", "class": "FDTD"} in products
    assert {"name": "mode", "class": "MODE"} in products
    assert {"name": "interconnect", "class": "INTERCONNECT"} in products
    assert {"name": "device", "class": "DEVICE"} in products


def test_list_sessions_starts_empty():
    assert list_sessions() == []


def test_product_class_rejects_unknown_product():
    with pytest.raises(LumericalSessionError):
        _product_class("unknown")


def test_product_class_rejects_empty_product():
    with pytest.raises(LumericalValidationError):
        _product_class("")


def test_json_safe_converts_basic_values():
    assert _json_safe({"x": [1, 2, 3]}) == {"x": [1, 2, 3]}


def test_configured_lumerical_install_dir(monkeypatch):
    monkeypatch.setenv(LUMERICAL_INSTALL_ENV, r"C:\Path\To\Lumerical\vXXX")

    assert _configured_lumerical_install_dir() == r"C:\Path\To\Lumerical\vXXX"


def test_validate_variable_name_rejects_whitespace():
    with pytest.raises(LumericalValidationError):
        _validate_variable_name("bad name")


def test_validated_existing_file_rejects_missing_path():
    with pytest.raises(LumericalValidationError):
        _validated_existing_file(r"C:\definitely\missing\file.lsf", "script")


def test_busy_session_blocks_new_calls():
    session_id = "busy-test"
    _SESSIONS[session_id] = {
        "id": session_id,
        "product": "fdtd",
        "session": object(),
        "hide": True,
        "project": None,
        "script": None,
        "busy": True,
        "last_error": None,
    }

    try:
        with pytest.raises(LumericalSessionError):
            _get_session(session_id)
    finally:
        _SESSIONS.pop(session_id, None)
