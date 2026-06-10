"""Regression tests — duplicate order detection and idempotency (5 tests)."""


class TestDuplicateDetection:
    def test_duplicate_client_order_id_returns_409(self, oms, new_order_payload):
        payload = new_order_payload(client_order_id="DUP-001")
        oms.create_order(payload)
        body, status = oms.create_order(payload)
        assert status == 409
        assert "duplicate" in body["error"].lower()

    def test_same_client_id_different_symbol_still_409(self, oms, new_order_payload):
        oms.create_order(new_order_payload(client_order_id="DUP-002", symbol="AAPL"))
        body, status = oms.create_order(new_order_payload(client_order_id="DUP-002", symbol="TSLA"))
        assert status == 409

    def test_unique_client_order_ids_both_succeed(self, oms, new_order_payload):
        _, s1 = oms.create_order(new_order_payload(client_order_id="UNIQ-001"))
        _, s2 = oms.create_order(new_order_payload(client_order_id="UNIQ-002"))
        assert s1 == 201
        assert s2 == 201

    def test_first_duplicate_does_not_affect_original(self, oms, new_order_payload):
        body1, _ = oms.create_order(new_order_payload(client_order_id="DUP-003"))
        oms.create_order(new_order_payload(client_order_id="DUP-003"))
        body_get, status = oms.get_order(body1["id"])
        assert status == 200
        assert body_get["status"] == "NEW"

    def test_list_does_not_return_duplicate_entries(self, oms, new_order_payload):
        oms.create_order(new_order_payload(client_order_id="LIST-001"))
        oms.create_order(new_order_payload(client_order_id="LIST-001"))  # duplicate, rejected
        orders, _ = oms.list_orders()
        ids = [o["client_order_id"] for o in orders]
        assert ids.count("LIST-001") == 1
