"""Base model for DNSE API responses."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class DnseBaseModel(BaseModel):
    """Base model with shared DNSE API configuration.

    Supports both snake_case Python attributes and camelCase JSON keys
    from the DNSE API. Use this as the base for all response models.

    Example:
        class OrderInfo(DnseBaseModel):
            order_id: str
            total_amount: float

        # Both work:
        OrderInfo(order_id="123", total_amount=100.0)
        OrderInfo(**{"orderId": "123", "totalAmount": 100.0})
    """

    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
        alias_generator=to_camel,
    )
