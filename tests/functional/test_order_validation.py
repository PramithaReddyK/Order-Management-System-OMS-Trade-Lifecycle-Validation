"""Functional tests — order validation (6 tests)."""


class TestOrderValidation:
    def test_invalid_side_returns_400(self, oms, new_order_payload):
        body, status = oms.create_order(new_order_payload(side="HOLD", client_order_id="VAL-001"))
        assert status == 400
        assert "side" in body["error"].lower()

    def test_invalid_order_type_returns_400(self, oms, new_order_payload):
        body, status = oms.create_order(
            new_order_payload(order_type="STOP", client_order_id="VAL-002")
        )
        assert status == 400

    def test_limit_order_without_price_returns_400(self, oms):
        body, status = oms.create_order(
            {
                "client_order_id": "VAL-003",
                "symbol": "AAPL",
                "side": "BUY",
                "quantity": 10,
                "order_type": "LIMIT",
                # no price
            }
        )
        assert status == 400

    def test_limit_order_with_zero_price_returns_400(self, oms, new_order_payload):
        body, status = oms.create_order(
            new_order_payload(price=0, client_order_id="VAL-004")
        )
        assert status == 400

    def test_empty_body_returns_400(self, oms):
        body, status = oms.create_order({})
        assert status == 400

    def test_get_nonexistent_order_returns_404(self, oms):
        body, status = oms.get_order(999999)
        assert status == 404
        assert "error" in body
