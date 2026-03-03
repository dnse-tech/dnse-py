"""Tests for DnseClient (synchronous)."""

import httpx
import pytest
import respx

from dnse.client import DnseClient
from dnse.exceptions import DnseAuthError

BASE_URL = "https://openapi.dnse.com.vn"


def test_get_success():
    with respx.mock(base_url=BASE_URL) as mock:
        mock.get("/v1/health").mock(return_value=httpx.Response(200, json={"status": "ok"}))
        with DnseClient() as client:
            response = client.get("/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_post_success():
    with respx.mock(base_url=BASE_URL) as mock:
        mock.post("/v1/orders").mock(return_value=httpx.Response(201, json={"id": "123"}))
        with DnseClient() as client:
            response = client.post("/v1/orders", json={"symbol": "VNM"})
    assert response.status_code == 201


def test_auth_error():
    with respx.mock(base_url=BASE_URL) as mock:
        mock.get("/v1/account").mock(return_value=httpx.Response(401, text="Unauthorized"))
        with DnseClient(api_key="bad-key") as client:
            with pytest.raises(DnseAuthError) as exc_info:
                client.get("/v1/account")
    assert exc_info.value.status_code == 401


def test_context_manager_closes_client():
    with respx.mock(base_url=BASE_URL):
        client = DnseClient()
        with client:
            pass
        # After exit, underlying client should be closed
        assert client._http_client.is_closed


def test_put_success():
    with respx.mock(base_url=BASE_URL) as mock:
        mock.put("/v1/orders/123").mock(return_value=httpx.Response(200, json={"updated": True}))
        with DnseClient() as client:
            response = client.put("/v1/orders/123", json={"qty": 10})
    assert response.status_code == 200


def test_delete_success():
    with respx.mock(base_url=BASE_URL) as mock:
        mock.delete("/v1/orders/123").mock(return_value=httpx.Response(204))
        with DnseClient() as client:
            response = client.delete("/v1/orders/123")
    assert response.status_code == 204


def test_custom_base_url():
    custom_url = "https://staging.dnse.com.vn"
    with respx.mock(base_url=custom_url) as mock:
        mock.get("/v1/ping").mock(return_value=httpx.Response(200))
        with DnseClient(base_url=custom_url) as client:
            response = client.get("/v1/ping")
    assert response.status_code == 200
