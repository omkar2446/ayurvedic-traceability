from app.main import app


def test_auth_login_route_is_registered() -> None:
    paths = {route.path for route in app.routes}

    assert "/api/auth/login" in paths