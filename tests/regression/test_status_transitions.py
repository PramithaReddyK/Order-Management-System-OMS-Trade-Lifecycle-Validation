"""Regression tests — state machine transition coverage (8 tests)."""
import pytest


# All valid transitions according to the OMS state machine
VALID_PATHS = [
    ("NEW", "PENDING_ROUTING"),
    ("NEW", "CANCELLED"),
    ("NEW", "REJECTED"),
    ("PENDING_ROUTING", "ROUTED"),
    ("PENDING_ROUTING", "CANCELLED"),
    ("PENDING_ROUTING", "REJECTED"),
    ("ROUTED", "EXECUTED"),
    ("ROUTED", "CANCELLED"),
    ("ROUTED", "REJECTED"),
]

# Transitions that must be rejected
INVALID_PATHS = [
    ("NEW", "ROUTED"),
    ("NEW", "EXECUTED"),
    ("PENDING_ROUTING", "EXECUTED"),
    ("EXECUTED", "CANCELLED"),
    ("EXECUTED", "REJECTED"),
    ("CANCELLED", "NEW"),
    ("CANCELLED", "PENDING_ROUTING"),
    ("REJECTED", "NEW"),
]


def _advance_to(oms, order_id: int, target: str):
    """Advance an order to a given status using valid transitions."""
    path_map = {
        "PENDING_ROUTING": ["PENDING_ROUTING"],
        "ROUTED": ["PENDING_ROUTING", "ROUTED"],
        "EXECUTED": ["PENDING_ROUTING", "ROUTED", "EXECUTED"],
        "CANCELLED": [],  # caller handles
        "REJECTED": [],
    }
    for step in path_map.get(target, []):
        extra = {"venue": "NYSE"} if step == "ROUTED" else {}
        oms.transition(order_id, step, **extra)


class TestStatusTransitions:
    @pytest.mark.parametrize("from_status,to_status", [
        ("NEW", "PENDING_ROUTING"),
        ("NEW", "CANCELLED"),
        ("PENDING_ROUTING", "ROUTED"),
        ("PENDING_ROUTING", "CANCELLED"),
        ("ROUTED", "EXECUTED"),
        ("ROUTED", "CANCELLED"),
        ("ROUTED", "REJECTED"),
    ])
    def test_valid_transition(self, oms, created_order, from_status, to_status):
        if from_status != "NEW":
            _advance_to(oms, created_order["id"], from_status)
        extra = {"venue": "NYSE"} if to_status == "ROUTED" else {}
        body, status = oms.transition(created_order["id"], to_status, **extra)
        assert status == 200, f"Expected 200 for {from_status}→{to_status}, got {status}: {body}"
        assert body["status"] == to_status

    @pytest.mark.parametrize("from_status,to_status", [
        ("NEW", "ROUTED"),
        ("NEW", "EXECUTED"),
        ("PENDING_ROUTING", "EXECUTED"),
    ])
    def test_invalid_transition_returns_422(self, oms, created_order, from_status, to_status):
        if from_status != "NEW":
            _advance_to(oms, created_order["id"], from_status)
        body, status = oms.transition(created_order["id"], to_status)
        assert status == 422, f"Expected 422 for {from_status}→{to_status}, got {status}"

    def test_terminal_executed_blocks_all_transitions(self, oms, created_order):
        _advance_to(oms, created_order["id"], "EXECUTED")
        for bad in ("CANCELLED", "REJECTED", "NEW", "PENDING_ROUTING"):
            _, status = oms.transition(created_order["id"], bad)
            assert status == 422

    def test_terminal_cancelled_blocks_all_transitions(self, oms, created_order):
        oms.cancel_order(created_order["id"])
        for bad in ("NEW", "PENDING_ROUTING", "EXECUTED"):
            _, status = oms.transition(created_order["id"], bad)
            assert status == 422
