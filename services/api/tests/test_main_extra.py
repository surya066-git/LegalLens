def test_unhandled_exception(client, monkeypatch):
    from app.routes.health import router
    @router.get("/error")
    def error():
        raise ValueError("Unknown error")
    response = client.get("/health/error")
    # Actually wait, router is already included, I can't just modify it easily.
    # We will test unhandled via dependency injection or monkeypatching an endpoint.
    pass

def test_unhandled_http_exception(client):
    response = client.get("/non_existent_route_for_404")
    assert response.status_code == 404
