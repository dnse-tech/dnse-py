"""Reference: AccountsResource — all methods.

No OTP required.

Run: python reference/accounts.py
"""

from dotenv import load_dotenv

load_dotenv()

import os  # noqa: E402

from dnse import DnseClient  # noqa: E402

ACCOUNT_NO = os.environ["DNSE_ACCOUNT_NO"]

with DnseClient(
    api_key=os.environ["DNSE_API_KEY"], api_secret=os.environ["DNSE_API_SECRET"]
) as client:
    # list() — all sub-accounts
    accounts = client.accounts.list()
    print("accounts.list():", accounts)

    # balances() — stock + derivative balances
    balances = client.accounts.balances(ACCOUNT_NO)
    print("\naccounts.balances():", balances)

    # loan_packages() — available margin packages (requires marketType and symbol)
    packages = client.accounts.loan_packages(ACCOUNT_NO, market_type="STOCK", symbol="HPG")
    print("\naccounts.loan_packages():", packages)

    # ppse() — pre-trade size estimation (requires symbol, price, marketType, loanPackageId)
    ppse = client.accounts.ppse(
        ACCOUNT_NO,
        symbol="HPG",
        price="27000",
        market_type="STOCK",
        loan_package_id=packages.loan_packages[0].id,
    )
    print("\naccounts.ppse():", ppse)
