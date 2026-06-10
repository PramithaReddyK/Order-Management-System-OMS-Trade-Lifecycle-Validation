"""SQL helpers for direct database assertions in integration tests."""
from __future__ import annotations

from sqlalchemy.orm import Session

from app.models import Order


def fetch_order_by_id(db: Session, order_id: int) -> Order | None:
    return db.get(Order, order_id)


def fetch_order_by_client_id(db: Session, client_order_id: str) -> Order | None:
    return db.query(Order).filter(Order.client_order_id == client_order_id).first()


def count_orders_by_status(db: Session, status: str) -> int:
    return db.query(Order).filter(Order.status == status).count()


def assert_db_matches_response(db: Session, response_body: dict) -> None:
    """Verify every field in the API response matches the DB record."""
    order = fetch_order_by_id(db, response_body["id"])
    assert order is not None, f"Order {response_body['id']} not found in DB"
    assert order.status == response_body["status"]
    assert order.symbol == response_body["symbol"]
    assert str(order.quantity) == response_body["quantity"]
    assert order.client_order_id == response_body["client_order_id"]
