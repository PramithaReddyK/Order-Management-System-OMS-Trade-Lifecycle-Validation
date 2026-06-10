"""Functional tests — order creation (8 tests)."""
import pytest


class TestOrderCreation:
    def test_create_limit_order_returns_201(self, oms, new_order_payload):
        body, status = oms.create_order(new_order_payload())
        assert status == 201
        assert body["status"] == "NEW"

    def test_create_market_order_no_price(self, oms, new_order_payload):
        body, status = oms.create_order(new_order_payload(order_type="MARKET", client_order_id="MKT-001"))
        assert status == 201
        assert body["order_type"] == "MARKET"
        assert body["price"] is None

    def test_response_contains_all_fields(self, oms, new_order_payload):
        body, _ = oms.create_order(new_order_payload(client_order_id="FIELD-001"))
        for field in ("id", "client_order_id", "symbol", "side", "quantity", "order_type", "status", "created_at"):
            assert field in body, f"Missing field: {field}"

    def test_symbol_stored_uppercase(self, oms, new_order_payload):
        body, status = oms.create_order(new_order_payload(symbol="aapl", client_order_id="CASE-001"))
        assert status == 201
        assert body["symbol"] == "AAPL"

    def test_create_sell_order(self, oms, new_order_payload):
        body, status = oms.create_order(
            new_order_payload(side="SELL", client_order_id="SELL-001", order_type="MARKET")
        )
        assert status == 201
        assert body["side"] == "SELL"

    def test_missing_required_field_returns_400(self, oms):
        body, status = oms.create_order({"symbol": "AAPL", "side": "BUY", "quantity": 10, "order_type": "MARKET"})
        assert status == 400
        assert "error" in body

    def test_zero_quantity_returns_400(self, oms, new_order_payload):
        body, status = oms.create_order(new_order_payload(quantity=0, client_order_id="QTY-001"))
        assert status == 400

    def test_negative_quantity_returns_400(self, oms, new_order_payload):
        body, status = oms.create_order(new_order_payload(quantity=-5, client_order_id="QTY-NEG-001"))
        assert status == 400
