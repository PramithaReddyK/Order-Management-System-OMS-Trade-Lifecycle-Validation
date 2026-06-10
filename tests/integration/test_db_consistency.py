"""Integration tests — API response vs database record consistency (6 tests)."""
from tests.utils.db_utils import (
    assert_db_matches_response,
    count_orders_by_status,
    fetch_order_by_client_id,
    fetch_order_by_id,
)


class TestDBConsistency:
    def test_created_order_persisted_in_db(self, oms, db_session, new_order_payload):
        body, _ = oms.create_order(new_order_payload(client_order_id="DB-001"))
        assert_db_matches_response(db_session, body)

    def test_status_transition_reflected_in_db(self, oms, db_session, created_order):
        oms.transition(created_order["id"], "PENDING_ROUTING")
        db_order = fetch_order_by_id(db_session, created_order["id"])
        db_session.refresh(db_order)
        assert db_order.status == "PENDING_ROUTING"

    def test_cancellation_reflected_in_db(self, oms, db_session, created_order):
        oms.cancel_order(created_order["id"])
        db_order = fetch_order_by_id(db_session, created_order["id"])
        db_session.refresh(db_order)
        assert db_order.status == "CANCELLED"

    def test_quantity_modification_reflected_in_db(self, oms, db_session, created_order):
        oms.update_order(created_order["id"], {"quantity": 999})
        db_order = fetch_order_by_id(db_session, created_order["id"])
        db_session.refresh(db_order)
        assert float(db_order.quantity) == 999

    def test_venue_stored_on_routing(self, oms, db_session, created_order):
        oms.transition(created_order["id"], "PENDING_ROUTING")
        oms.transition(created_order["id"], "ROUTED", venue="CBOE")
        db_order = fetch_order_by_id(db_session, created_order["id"])
        db_session.refresh(db_order)
        assert db_order.venue == "CBOE"

    def test_duplicate_rejection_does_not_create_db_record(self, oms, db_session, new_order_payload):
        payload = new_order_payload(client_order_id="DB-DUP-001")
        oms.create_order(payload)
        oms.create_order(payload)  # duplicate
        count = db_session.query(__import__("app.models", fromlist=["Order"]).Order).filter_by(
            client_order_id="DB-DUP-001"
        ).count()
        assert count == 1
