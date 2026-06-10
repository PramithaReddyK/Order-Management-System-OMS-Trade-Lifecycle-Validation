"""Thin wrapper around the Flask test client for cleaner test assertions."""
from __future__ import annotations

from typing import Any


class OMSClient:
    def __init__(self, client):
        self._client = client

    def create_order(self, payload: dict) -> tuple[dict, int]:
        r = self._client.post("/orders", json=payload)
        return r.get_json(), r.status_code

    def get_order(self, order_id: int) -> tuple[dict, int]:
        r = self._client.get(f"/orders/{order_id}")
        return r.get_json(), r.status_code

    def list_orders(self, status: str | None = None) -> tuple[list, int]:
        url = "/orders" if not status else f"/orders?status={status}"
        r = self._client.get(url)
        return r.get_json(), r.status_code

    def update_order(self, order_id: int, payload: dict) -> tuple[dict, int]:
        r = self._client.patch(f"/orders/{order_id}", json=payload)
        return r.get_json(), r.status_code

    def cancel_order(self, order_id: int) -> tuple[dict, int]:
        r = self._client.delete(f"/orders/{order_id}")
        return r.get_json(), r.status_code

    def transition(self, order_id: int, status: str, **extra: Any) -> tuple[dict, int]:
        return self.update_order(order_id, {"status": status, **extra})
