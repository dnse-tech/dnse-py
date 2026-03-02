"""Tests for AsyncDnseClient (asynchronous)."""

import httpx
import pytest
import respx

from dnse.async_client import AsyncDnseClient
from dnse.exceptions import DnseAuthError

BASE_URL = "https://openapi.dnse.com.vn"


async def test_async_get_success():
    with respx.mock(base_url=BASE_URL) as mock:
        mock.get("/v1/health").mock(return_value=httpx.Response(200, json={"status": "ok"}))
        async with AsyncDnseClient() as client:
            response = await client.get("/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


async def test_async_post_success():
    with respx.mock(base_url=BASE_URL) as mock:
        mock.post("/v1/orders").mock(return_value=httpx.Response(201, json={"id": "456"}))
        async with AsyncDnseClient() as client:
            response = await client.post("/v1/orders", json={"symbol": "FPT"})
    assert response.status_code == 201


async def test_async_auth_error():
    with respx.mock(base_url=BASE_URL) as mock:
        mock.get("/v1/account").mock(return_value=httpx.Response(401, text="Unauthorized"))
        async with AsyncDnseClient(api_key="bad-key") as client:
            with pytest.raises(DnseAuthError) as exc_info:
                await client.get("/v1/account")
    assert exc_info.value.status_code == 401


async def test_async_put_success():
    with respx.mock(base_url=BASE_URL) as mock:
        mock.put("/v1/orders/123").mock(return_value=httpx.Response(200, json={"updated": True}))
        async with AsyncDnseClient() as client:
            response = await client.put("/v1/orders/123", json={"qty": 10})
    assert response.status_code == 200


async def test_async_delete_success():
    with respx.mock(base_url=BASE_URL) as mock:
        mock.delete("/v1/orders/123").mock(return_value=httpx.Response(204))
        async with AsyncDnseClient() as client:
            response = await client.delete("/v1/orders/123")
    assert response.status_code == 204


async def test_async_context_manager_closes_client():
    with respx.mock(base_url=BASE_URL):
        client = AsyncDnseClient()
        async with client:
            pass
        assert client._client.is_closed
