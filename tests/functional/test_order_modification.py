"""Functional tests — order modification (6 tests)."""


class TestOrderModification:
    def test_modify_quantity_in_new_status(self, oms, created_order):
        body, status = oms.update_order(created_order["id"], {"quantity": 200})
        assert status == 200
        assert body["quantity"] == "200"

    def test_modify_price_in_new_status(self, oms, created_order):
        body, status = oms.update_order(created_order["id"], {"price": "175.50"})
        assert status == 200
        assert float(body["price"]) == 175.50

    def test_modify_quantity_in_pending_routing(self, oms, created_order):
        oms.transition(created_order["id"], "PENDING_ROUTING")
        body, status = oms.update_order(created_order["id"], {"quantity": 50})
        assert status == 200
        assert body["quantity"] == "50"

    def test_cannot_modify_routed_order(self, oms, created_order):
        oms.transition(created_order["id"], "PENDING_ROUTING")
        oms.transition(created_order["id"], "ROUTED", venue="NYSE")
        body, status = oms.update_order(created_order["id"], {"quantity": 300})
        assert status == 422

    def test_cannot_modify_executed_order(self, oms, created_order):
        oms.transition(created_order["id"], "PENDING_ROUTING")
        oms.transition(created_order["id"], "ROUTED", venue="NYSE")
        oms.transition(created_order["id"], "EXECUTED")
        body, status = oms.update_order(created_order["id"], {"quantity": 300})
        assert status == 422

    def test_modify_nonexistent_order_returns_404(self, oms):
        body, status = oms.update_order(999999, {"quantity": 10})
        assert status == 404
