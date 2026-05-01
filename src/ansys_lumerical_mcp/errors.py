class LumericalMcpError(Exception):
    """Base exception for server-facing Lumerical errors."""

    code = "lumerical_error"

    def to_dict(self) -> dict[str, str]:
        return {"code": self.code, "message": str(self)}


class LumericalImportError(LumericalMcpError):
    """Raised when ansys-lumerical-core cannot be imported."""

    code = "lumerical_import_error"


class LumericalSessionError(LumericalMcpError):
    """Raised when a requested Lumerical session cannot be used."""

    code = "lumerical_session_error"


class LumericalValidationError(LumericalMcpError):
    """Raised when user-provided MCP tool input is invalid."""

    code = "lumerical_validation_error"


class LumericalApiCallError(LumericalMcpError):
    """Raised when the Lumerical API rejects or fails a call."""

    code = "lumerical_api_call_error"
