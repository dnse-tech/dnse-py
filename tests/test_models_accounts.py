"""Tests for account-related models."""

from dnse.models.accounts import (
    AccountBalanceResponse,
    AccountsResponse,
    AccountSubItem,
    LoanPackage,
    LoanPackageResponse,
    PpseResponse,
    StockBalance,
)


def test_account_sub_item_creation():
    """AccountSubItem can be created with id and deal_account."""
    item = AccountSubItem(id="0003979888", deal_account=True)
    assert item.id == "0003979888"
    assert item.deal_account is True


def test_account_sub_item_model_validate_camel_case():
    """AccountSubItem.model_validate with camelCase 'dealAccount'."""
    item = AccountSubItem.model_validate({"id": "123", "dealAccount": True})
    assert item.id == "123"
    assert item.deal_account is True


def test_accounts_response_creation():
    """AccountsResponse can be created with accounts list."""
    accounts = [
        AccountSubItem(id="001", deal_account=True),
        AccountSubItem(id="002", deal_account=False),
    ]
    resp = AccountsResponse(accounts=accounts, custody_code="X", investor_id="inv123")
    assert len(resp.accounts) == 2
    assert resp.accounts[0].id == "001"
    assert resp.custody_code == "X"
    assert resp.investor_id == "inv123"


def test_accounts_response_model_validate():
    """AccountsResponse.model_validate with camelCase JSON."""
    resp = AccountsResponse.model_validate(
        {
            "accounts": [
                {"id": "123", "dealAccount": True},
                {"id": "456", "dealAccount": False},
            ],
            "custodyCode": "CODE",
            "investorId": "INV123",
            "name": "John Doe",
        }
    )
    assert len(resp.accounts) == 2
    assert resp.accounts[0].id == "123"
    assert resp.custody_code == "CODE"
    assert resp.investor_id == "INV123"
    assert resp.name == "John Doe"


def test_stock_balance_creation():
    """StockBalance can be created with various balance fields."""
    balance = StockBalance(
        available_cash=1000,
        total_cash=5000,
        withdrawable_cash=900,
        total_debt=2000,
    )
    assert balance.available_cash == 1000
    assert balance.total_cash == 5000
    assert balance.withdrawable_cash == 900
    assert balance.total_debt == 2000


def test_stock_balance_model_validate_camel_case():
    """StockBalance.model_validate with camelCase JSON."""
    balance = StockBalance.model_validate(
        {
            "availableCash": 1000,
            "totalCash": 5000,
            "withdrawableCash": 900,
            "totalDebt": 2000,
            "cashDividendReceiving": 100,
            "depositFeeAmount": 50,
            "depositInterest": 25,
        }
    )
    assert balance.available_cash == 1000
    assert balance.total_cash == 5000
    assert balance.cash_dividend_receiving == 100
    assert balance.deposit_fee_amount == 50


def test_account_balance_response_creation():
    """AccountBalanceResponse can be created with stock balance."""
    stock = StockBalance(available_cash=1000, total_cash=5000)
    resp = AccountBalanceResponse(stock=stock)
    assert resp.stock is not None
    assert resp.stock.available_cash == 1000


def test_account_balance_response_model_validate():
    """AccountBalanceResponse.model_validate with camelCase JSON."""
    resp = AccountBalanceResponse.model_validate(
        {
            "stock": {
                "availableCash": 1000,
                "totalCash": 5000,
                "withdrawableCash": 900,
            }
        }
    )
    assert resp.stock is not None
    assert resp.stock.available_cash == 1000
    assert resp.stock.total_cash == 5000


def test_loan_package_creation():
    """LoanPackage can be created with loan details."""
    pkg = LoanPackage(
        id=1,
        name="Standard Loan",
        interest_rate=3.5,
        maintenance_rate=2.0,
        type="STOCK",
    )
    assert pkg.id == 1
    assert pkg.name == "Standard Loan"
    assert pkg.interest_rate == 3.5
    assert pkg.maintenance_rate == 2.0


def test_loan_package_model_validate_camel_case():
    """LoanPackage.model_validate with camelCase JSON."""
    pkg = LoanPackage.model_validate(
        {
            "id": 2,
            "name": "Premium Loan",
            "interestRate": 2.5,
            "initialRate": 2.0,
            "maintenanceRate": 1.5,
            "liquidRate": 0.5,
            "type": "STOCK",
        }
    )
    assert pkg.id == 2
    assert pkg.interest_rate == 2.5
    assert pkg.initial_rate == 2.0
    assert pkg.maintenance_rate == 1.5
    assert pkg.liquid_rate == 0.5


def test_loan_package_response_creation():
    """LoanPackageResponse can be created with loan packages list."""
    packages = [
        LoanPackage(id=1, name="Loan 1"),
        LoanPackage(id=2, name="Loan 2"),
    ]
    resp = LoanPackageResponse(loan_packages=packages)
    assert len(resp.loan_packages) == 2


def test_loan_package_response_empty_list():
    """LoanPackageResponse.model_validate with empty loan packages."""
    resp = LoanPackageResponse.model_validate({"loanPackages": []})
    assert resp.loan_packages == []


def test_ppse_response_creation():
    """PpseResponse can be created with price and quantities."""
    resp = PpseResponse(price=27000.0, qmax_buy=100, qmax_sell=150)
    assert resp.price == 27000.0
    assert resp.qmax_buy == 100
    assert resp.qmax_sell == 150


def test_ppse_response_model_validate_camel_case():
    """PpseResponse.model_validate with camelCase JSON."""
    resp = PpseResponse.model_validate(
        {"price": 27600.0, "qmaxBuy": 200, "qmaxSell": 300}
    )
    assert resp.price == 27600.0
    assert resp.qmax_buy == 200
    assert resp.qmax_sell == 300


def test_ppse_response_partial_fields():
    """PpseResponse works with only some fields set."""
    resp = PpseResponse.model_validate({"price": 28000.0})
    assert resp.price == 28000.0
    assert resp.qmax_buy is None
    assert resp.qmax_sell is None
