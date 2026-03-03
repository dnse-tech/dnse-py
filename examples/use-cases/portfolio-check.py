"""Portfolio Check — list accounts and balances.

No OTP required.

Setup: cp .env.example .env → fill credentials → pip install "dnse[examples]"
Run:   python use-cases/portfolio-check.py
"""

from dotenv import load_dotenv

load_dotenv()

import os  # noqa: E402

from dnse import DnseClient  # noqa: E402

with DnseClient(
    api_key=os.environ["DNSE_API_KEY"], api_secret=os.environ["DNSE_API_SECRET"]
) as client:
    accounts = client.accounts.list()
    print(f"Investor ID: {accounts.investor_id}")
    for acct in accounts.accounts:
        balances = client.accounts.balances(acct.id)
        print(
            f"\nAccount {acct.id} (deal={acct.deal_account} derivative={acct.derivative_account}):"
        )
        print(f"  Balances: {balances}")
