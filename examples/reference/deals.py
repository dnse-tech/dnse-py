"""Reference: DealsResource — all methods.

No OTP required.

Run: python reference/deals.py
"""

from dotenv import load_dotenv

load_dotenv()

import os  # noqa: E402

from dnse import DnseClient  # noqa: E402

ACCOUNT_NO = os.environ["DNSE_ACCOUNT_NO"]

with DnseClient(
    api_key=os.environ["DNSE_API_KEY"], api_secret=os.environ["DNSE_API_SECRET"]
) as client:
    deals = client.deals.list(ACCOUNT_NO)
    print("deals.list():", deals)
