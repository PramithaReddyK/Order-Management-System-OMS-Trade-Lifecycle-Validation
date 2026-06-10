"""Functional tests — order cancellation (5 tests)."""


class TestOrderCancellation:
    def test_cancel_new_order(self, oms, created_order):
        body, status = oms.cancel_order(created_order["id"])
        assert status == 200
        assert body["status"] == "CANCELLED"

    def test_cancel_pending_routing_order(self, oms, created_order):
        oms.transition(created_order["id"], "PENDING_ROUTING")
        body, status = oms.cancel_order(created_order["id"])
        assert status == 200
        assert body["status"] == "CANCELLED"

    def test_cancel_routed_order(self, oms, created_order):
        oms.transition(created_order["id"], "PENDING_ROUTING")
        oms.transition(created_order["id"], "ROUTED", venue="NYSE")
        body, status = oms.cancel_order(created_order["id"])
        assert status == 200
        assert body["status"] == "CANCELLED"

    def test_cannot_cancel_executed_order(self, oms, created_order):
        oms.transition(created_order["id"], "PENDING_ROUTING")
        oms.transition(created_order["id"], "ROUTED", venue="NYSE")
        oms.transition(created_order["id"], "EXECUTED")
        body, status = oms.cancel_order(created_order["id"])
        assert status == 422

    def test_cancel_nonexistent_order_returns_404(self, oms):
        body, status = oms.cancel_order(999999)
        assert status == 404
