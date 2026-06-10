"""Functional tests — order execution (6 tests)."""


def _route_order(oms, order_id: int):
    oms.transition(order_id, "PENDING_ROUTING")
    oms.transition(order_id, "ROUTED", venue="NYSE")


class TestOrderExecution:
    def test_execute_routed_order(self, oms, created_order):
        _route_order(oms, created_order["id"])
        body, status = oms.transition(created_order["id"], "EXECUTED")
        assert status == 200
        assert body["status"] == "EXECUTED"

    def test_executed_order_is_terminal(self, oms, created_order):
        _route_order(oms, created_order["id"])
        oms.transition(created_order["id"], "EXECUTED")
        body, status = oms.transition(created_order["id"], "CANCELLED")
        assert status == 422

    def test_cannot_execute_new_order(self, oms, created_order):
        body, status = oms.transition(created_order["id"], "EXECUTED")
        assert status == 422

    def test_cannot_execute_cancelled_order(self, oms, created_order):
        oms.cancel_order(created_order["id"])
        body, status = oms.transition(created_order["id"], "EXECUTED")
        assert status == 422

    def test_executed_order_fields_preserved(self, oms, created_order):
        _route_order(oms, created_order["id"])
        body, _ = oms.transition(created_order["id"], "EXECUTED")
        assert body["symbol"] == created_order["symbol"]
        assert body["quantity"] == created_order["quantity"]
        assert body["client_order_id"] == created_order["client_order_id"]

    def test_get_executed_order_returns_correct_status(self, oms, created_order):
        _route_order(oms, created_order["id"])
        oms.transition(created_order["id"], "EXECUTED")
        body, status = oms.get_order(created_order["id"])
        assert status == 200
        assert body["status"] == "EXECUTED"
