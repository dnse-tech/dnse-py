"""Accounts resource: sub-account info, balances, loan packages, PPSE."""

from __future__ import annotations

from typing import TYPE_CHECKING

from dnse.models.accounts import (
    AccountBalanceResponse,
    AccountsResponse,
    LoanPackageResponse,
    PpseResponse,
)

if TYPE_CHECKING:
    from dnse._base_client import BaseClient
    from dnse.async_client import AsyncDnseClient


class AccountsResource:
    """Sync resource for account endpoints."""

    def __init__(self, client: BaseClient) -> None:
        """Initialize with a sync client reference."""
        self._client = client

    def list(self) -> AccountsResponse:
        """List all sub-accounts for the authenticated investor.

        Returns:
            AccountsResponse with accounts list and investor info.
        """
        path = "/accounts"
        headers = self._client._request_headers("GET", path)
        response = self._client._send("GET", path, headers=headers)
        return self._client._parse(response, AccountsResponse)

    def balances(self, account_no: str) -> AccountBalanceResponse:
        """Get balances for a sub-account.

        Args:
            account_no: Sub-account number.

        Returns:
            AccountBalanceResponse with stock and derivative balances.
        """
        path = f"/accounts/{account_no}/balances"
        headers = self._client._request_headers("GET", path)
        response = self._client._send("GET", path, headers=headers)
        return self._client._parse(response, AccountBalanceResponse)

    def loan_packages(self, account_no: str) -> LoanPackageResponse:
        """Get available loan/margin packages for a sub-account.

        Args:
            account_no: Sub-account number.

        Returns:
            LoanPackageResponse with list of available packages.
        """
        path = f"/accounts/{account_no}/loan-packages"
        headers = self._client._request_headers("GET", path)
        response = self._client._send("GET", path, headers=headers)
        return self._client._parse(response, LoanPackageResponse)

    def ppse(self, account_no: str, *, symbol: str, price: str) -> PpseResponse:
        """Get pre-trade price/size estimation (PPSE) for a symbol.

        Args:
            account_no: Sub-account number.
            symbol: Security symbol (e.g. "HPG").
            price: Price string for estimation.

        Returns:
            PpseResponse with max buy/sell quantities.
        """
        path = f"/accounts/{account_no}/ppse"
        headers = self._client._request_headers("GET", path)
        response = self._client._send(
            "GET", path, headers=headers, params={"symbol": symbol, "price": price}
        )
        return self._client._parse(response, PpseResponse)


class AsyncAccountsResource:
    """Async resource for account endpoints."""

    def __init__(self, client: AsyncDnseClient) -> None:
        """Initialize with an async client reference."""
        self._client = client

    async def list(self) -> AccountsResponse:
        """List all sub-accounts (async)."""
        path = "/accounts"
        headers = self._client._request_headers("GET", path)
        response = await self._client._async_send("GET", path, headers=headers)
        return self._client._parse(response, AccountsResponse)

    async def balances(self, account_no: str) -> AccountBalanceResponse:
        """Get balances for a sub-account (async)."""
        path = f"/accounts/{account_no}/balances"
        headers = self._client._request_headers("GET", path)
        response = await self._client._async_send("GET", path, headers=headers)
        return self._client._parse(response, AccountBalanceResponse)

    async def loan_packages(self, account_no: str) -> LoanPackageResponse:
        """Get loan packages for a sub-account (async)."""
        path = f"/accounts/{account_no}/loan-packages"
        headers = self._client._request_headers("GET", path)
        response = await self._client._async_send("GET", path, headers=headers)
        return self._client._parse(response, LoanPackageResponse)

    async def ppse(self, account_no: str, *, symbol: str, price: str) -> PpseResponse:
        """Get PPSE for a symbol (async)."""
        path = f"/accounts/{account_no}/ppse"
        headers = self._client._request_headers("GET", path)
        response = await self._client._async_send(
            "GET", path, headers=headers, params={"symbol": symbol, "price": price}
        )
        return self._client._parse(response, PpseResponse)
