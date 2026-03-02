"""Tests for Pydantic response models."""

from dnse.models.base import DnseBaseModel


class SampleModel(DnseBaseModel):
    order_id: str
    total_amount: float


def test_base_model_snake_case():
    m = SampleModel(order_id="abc", total_amount=99.5)
    assert m.order_id == "abc"
    assert m.total_amount == 99.5


def test_base_model_camel_alias():
    m = SampleModel.model_validate({"orderId": "xyz", "totalAmount": 50.0})
    assert m.order_id == "xyz"
    assert m.total_amount == 50.0


def test_base_model_populate_by_name():
    # populate_by_name=True means snake_case also works when alias is set
    m = SampleModel.model_validate({"order_id": "123", "total_amount": 10.0})
    assert m.order_id == "123"
