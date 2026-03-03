"""Account-related response models for DNSE SDK."""

from __future__ import annotations

from dnse.models.base import DnseBaseModel


class AccountSubItem(DnseBaseModel):
    """A single sub-account entry from the accounts list."""

    id: str  # sub-account number, e.g. "0003979888"
    deal_account: bool | None = None
    derivative_account: bool | None = None


class AccountsResponse(DnseBaseModel):
    """Response from GET /accounts."""

    accounts: list[AccountSubItem] = []
    custody_code: str | None = None
    investor_id: str | None = None
    name: str | None = None


class StockBalance(DnseBaseModel):
    """Stock sub-account balance fields."""

    available_cash: int | None = None
    cash_dividend_receiving: int | None = None
    deposit_fee_amount: int | None = None
    deposit_interest: int | None = None
    total_cash: int | None = None
    total_debt: int | None = None
    withdrawable_cash: int | None = None


class AccountBalanceResponse(DnseBaseModel):
    """Response from GET /accounts/{accountNo}/balances."""

    stock: StockBalance | None = None


class LoanPackage(DnseBaseModel):
    """A margin/loan package available for an account."""

    id: int | None = None
    name: str | None = None
    interest_rate: float | None = None
    initial_rate: float | None = None
    maintenance_rate: float | None = None
    liquid_rate: float | None = None
    type: str | None = None


class LoanPackageResponse(DnseBaseModel):
    """Response from GET /accounts/{accountNo}/loan-packages."""

    loan_packages: list[LoanPackage] = []


class PpseResponse(DnseBaseModel):
    """Response from GET /accounts/{accountNo}/ppse (pre-trade price/size estimation)."""

    price: float | None = None
    qmax_buy: int | None = None
    qmax_sell: int | None = None
