"""Tests for resource initialization and access patterns."""

from dnse.async_client import AsyncDnseClient
from dnse.client import DnseClient
from dnse.resources.accounts import AccountsResource, AsyncAccountsResource
from dnse.resources.deals import AsyncDealsResource, DealsResource
from dnse.resources.market import AsyncMarketResource, MarketResource
from dnse.resources.orders import AsyncOrdersResource, OrdersResource
from dnse.resources.registration import AsyncRegistrationResource, RegistrationResource

BASE_URL = "https://openapi.dnse.com.vn"


class TestDnseClientResourcesExist:
    """Test that DnseClient resources exist and are properly cached."""

    def test_registration_resource_type(self):
        """client.registration returns RegistrationResource."""
        with DnseClient() as client:
            assert isinstance(client.registration, RegistrationResource)

    def test_accounts_resource_type(self):
        """client.accounts returns AccountsResource."""
        with DnseClient() as client:
            assert isinstance(client.accounts, AccountsResource)

    def test_orders_resource_type(self):
        """client.orders returns OrdersResource."""
        with DnseClient() as client:
            assert isinstance(client.orders, OrdersResource)

    def test_deals_resource_type(self):
        """client.deals returns DealsResource."""
        with DnseClient() as client:
            assert isinstance(client.deals, DealsResource)

    def test_market_resource_type(self):
        """client.market returns MarketResource."""
        with DnseClient() as client:
            assert isinstance(client.market, MarketResource)

    def test_registration_is_cached(self):
        """client.registration returns same instance (cached_property)."""
        with DnseClient() as client:
            reg1 = client.registration
            reg2 = client.registration
            assert reg1 is reg2

    def test_accounts_is_cached(self):
        """client.accounts returns same instance (cached_property)."""
        with DnseClient() as client:
            acc1 = client.accounts
            acc2 = client.accounts
            assert acc1 is acc2

    def test_orders_is_cached(self):
        """client.orders returns same instance (cached_property)."""
        with DnseClient() as client:
            ord1 = client.orders
            ord2 = client.orders
            assert ord1 is ord2

    def test_deals_is_cached(self):
        """client.deals returns same instance (cached_property)."""
        with DnseClient() as client:
            deals1 = client.deals
            deals2 = client.deals
            assert deals1 is deals2

    def test_market_is_cached(self):
        """client.market returns same instance (cached_property)."""
        with DnseClient() as client:
            mkt1 = client.market
            mkt2 = client.market
            assert mkt1 is mkt2

    def test_registration_client_reference(self):
        """RegistrationResource has reference to client."""
        with DnseClient() as client:
            assert client.registration._client is client

    def test_accounts_client_reference(self):
        """AccountsResource has reference to client."""
        with DnseClient() as client:
            assert client.accounts._client is client

    def test_orders_client_reference(self):
        """OrdersResource has reference to client."""
        with DnseClient() as client:
            assert client.orders._client is client

    def test_deals_client_reference(self):
        """DealsResource has reference to client."""
        with DnseClient() as client:
            assert client.deals._client is client

    def test_market_client_reference(self):
        """MarketResource has reference to client."""
        with DnseClient() as client:
            assert client.market._client is client


class TestAsyncDnseClientResourcesExist:
    """Test that AsyncDnseClient resources exist and are properly cached."""

    async def test_registration_resource_type(self):
        """async client.registration returns AsyncRegistrationResource."""
        async with AsyncDnseClient() as client:
            assert isinstance(client.registration, AsyncRegistrationResource)

    async def test_accounts_resource_type(self):
        """async client.accounts returns AsyncAccountsResource."""
        async with AsyncDnseClient() as client:
            assert isinstance(client.accounts, AsyncAccountsResource)

    async def test_orders_resource_type(self):
        """async client.orders returns AsyncOrdersResource."""
        async with AsyncDnseClient() as client:
            assert isinstance(client.orders, AsyncOrdersResource)

    async def test_deals_resource_type(self):
        """async client.deals returns AsyncDealsResource."""
        async with AsyncDnseClient() as client:
            assert isinstance(client.deals, AsyncDealsResource)

    async def test_market_resource_type(self):
        """async client.market returns AsyncMarketResource."""
        async with AsyncDnseClient() as client:
            assert isinstance(client.market, AsyncMarketResource)

    async def test_registration_is_cached(self):
        """async client.registration returns same instance."""
        async with AsyncDnseClient() as client:
            reg1 = client.registration
            reg2 = client.registration
            assert reg1 is reg2

    async def test_accounts_is_cached(self):
        """async client.accounts returns same instance."""
        async with AsyncDnseClient() as client:
            acc1 = client.accounts
            acc2 = client.accounts
            assert acc1 is acc2

    async def test_orders_is_cached(self):
        """async client.orders returns same instance."""
        async with AsyncDnseClient() as client:
            ord1 = client.orders
            ord2 = client.orders
            assert ord1 is ord2

    async def test_deals_is_cached(self):
        """async client.deals returns same instance."""
        async with AsyncDnseClient() as client:
            deals1 = client.deals
            deals2 = client.deals
            assert deals1 is deals2

    async def test_market_is_cached(self):
        """async client.market returns same instance."""
        async with AsyncDnseClient() as client:
            mkt1 = client.market
            mkt2 = client.market
            assert mkt1 is mkt2

    async def test_registration_client_reference(self):
        """AsyncRegistrationResource has reference to client."""
        async with AsyncDnseClient() as client:
            assert client.registration._client is client

    async def test_accounts_client_reference(self):
        """AsyncAccountsResource has reference to client."""
        async with AsyncDnseClient() as client:
            assert client.accounts._client is client

    async def test_orders_client_reference(self):
        """AsyncOrdersResource has reference to client."""
        async with AsyncDnseClient() as client:
            assert client.orders._client is client

    async def test_deals_client_reference(self):
        """AsyncDealsResource has reference to client."""
        async with AsyncDnseClient() as client:
            assert client.deals._client is client

    async def test_market_client_reference(self):
        """AsyncMarketResource has reference to client."""
        async with AsyncDnseClient() as client:
            assert client.market._client is client
