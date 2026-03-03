"""Tests for StreamEncoder JSON and msgpack encode/decode."""

import pytest

from dnse.stream._stream_encoding import StreamEncoder
from dnse.stream.exceptions import DnseStreamProtocolError


def test_json_encode_decode_roundtrip():
    enc = StreamEncoder("json")
    obj = {"action": "auth", "key": "val", "num": 42}
    assert enc.decode(enc.encode(obj)) == obj


def test_json_encode_returns_string():
    assert isinstance(StreamEncoder("json").encode({"x": 1}), str)


def test_json_decode_malformed_raises_protocol_error():
    with pytest.raises(DnseStreamProtocolError):
        StreamEncoder("json").decode("not valid json {{{")


def test_invalid_encoding_raises_value_error():
    with pytest.raises(ValueError, match="encoding must be one of"):
        StreamEncoder("xml")


def test_query_param_json():
    assert StreamEncoder("json").query_param == "json"


def test_query_param_msgpack():
    pytest.importorskip("msgpack")
    assert StreamEncoder("msgpack").query_param == "msgpack"


def test_msgpack_encode_decode_roundtrip():
    pytest.importorskip("msgpack")
    enc = StreamEncoder("msgpack")
    obj = {"T": "t", "symbol": "VIC", "price": 98.5}
    assert enc.decode(enc.encode(obj)) == obj


def test_msgpack_encode_returns_bytes():
    pytest.importorskip("msgpack")
    assert isinstance(StreamEncoder("msgpack").encode({"x": 1}), bytes)
