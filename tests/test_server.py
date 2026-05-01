from ansys_lumerical_mcp.server import SERVER_NAME, create_server


def test_create_server():
    server = create_server()

    assert SERVER_NAME == "ansys-lumerical-mcp"
    assert server is not None
