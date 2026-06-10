"""Functional tests — order routing (5 tests)."""


class TestOrderRouting:
    def test_route_order_transitions_to_pending_routing(self, oms, created_order):
        body, status = oms.transition(created_order["id"], "PENDING_ROUTING")
        assert status == 200
        assert body["status"] == "PENDING_ROUTING"

    def test_route_order_transitions_to_routed(self, oms, created_order):
        oms.transition(created_order["id"], "PENDING_ROUTING")
        body, status = oms.transition(created_order["id"], "ROUTED", venue="NYSE")
        assert status == 200
        assert body["status"] == "ROUTED"
        assert body["venue"] == "NYSE"

    def test_venue_stored_on_routing(self, oms, created_order):
        oms.transition(created_order["id"], "PENDING_ROUTING")
        body, _ = oms.transition(created_order["id"], "ROUTED", venue="NASDAQ")
        assert body["venue"] == "NASDAQ"

    def test_cannot_skip_routing_step(self, oms, created_order):
        # NEW → ROUTED is not a valid transition
        body, status = oms.transition(created_order["id"], "ROUTED")
        assert status == 422

    def test_routing_nonexistent_order_returns_404(self, oms):
        body, status = oms.transition(99999, "PENDING_ROUTING")
        assert status == 404
