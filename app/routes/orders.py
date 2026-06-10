from datetime import datetime, timezone

from flask import Blueprint, g, jsonify, request
from sqlalchemy.exc import IntegrityError

from app.models import MODIFIABLE_STATUSES, VALID_TRANSITIONS, Order, OrderStatus

orders_bp = Blueprint("orders", __name__, url_prefix="/orders")

REQUIRED_CREATE_FIELDS = {"client_order_id", "symbol", "side", "quantity", "order_type"}
VALID_SIDES = {"BUY", "SELL"}
VALID_ORDER_TYPES = {"MARKET", "LIMIT"}


def _db():
    return g.db


@orders_bp.post("")
def create_order():
    data = request.get_json(silent=True) or {}

    missing = REQUIRED_CREATE_FIELDS - data.keys()
    if missing:
        return jsonify({"error": f"Missing fields: {sorted(missing)}"}), 400

    if data["side"].upper() not in VALID_SIDES:
        return jsonify({"error": f"Invalid side: {data['side']}"}), 400

    if data["order_type"].upper() not in VALID_ORDER_TYPES:
        return jsonify({"error": f"Invalid order_type: {data['order_type']}"}), 400

    try:
        qty = float(data["quantity"])
        if qty <= 0:
            raise ValueError
    except (ValueError, TypeError):
        return jsonify({"error": "quantity must be a positive number"}), 400

    if data["order_type"].upper() == "LIMIT":
        try:
            price = float(data.get("price", 0))
            if price <= 0:
                raise ValueError
        except (ValueError, TypeError):
            return jsonify({"error": "LIMIT orders require a positive price"}), 400

    order = Order(
        client_order_id=data["client_order_id"],
        symbol=data["symbol"].upper(),
        side=data["side"].upper(),
        quantity=data["quantity"],
        price=data.get("price"),
        order_type=data["order_type"].upper(),
        status=OrderStatus.NEW,
    )
    db = _db()
    db.add(order)
    try:
        db.flush()
    except IntegrityError:
        db.rollback()
        return jsonify({"error": "Duplicate client_order_id"}), 409

    db.commit()
    db.refresh(order)
    return jsonify(order.to_dict()), 201


@orders_bp.get("")
def list_orders():
    db = _db()
    status_filter = request.args.get("status")
    q = db.query(Order)
    if status_filter:
        q = q.filter(Order.status == status_filter.upper())
    orders = q.order_by(Order.created_at.desc()).all()
    return jsonify([o.to_dict() for o in orders]), 200


@orders_bp.get("/<int:order_id>")
def get_order(order_id: int):
    db = _db()
    order = db.get(Order, order_id)
    if not order:
        return jsonify({"error": "Order not found"}), 404
    return jsonify(order.to_dict()), 200


@orders_bp.patch("/<int:order_id>")
def update_order(order_id: int):
    db = _db()
    order = db.get(Order, order_id)
    if not order:
        return jsonify({"error": "Order not found"}), 404

    data = request.get_json(silent=True) or {}

    # Status transition
    if "status" in data:
        new_status = data["status"].upper()
        allowed = VALID_TRANSITIONS.get(order.status, set())
        if new_status not in allowed:
            return jsonify(
                {"error": f"Cannot transition from {order.status} to {new_status}"}
            ), 422

        order.status = new_status
        if "venue" in data:
            order.venue = data["venue"]
        if "rejection_reason" in data:
            order.rejection_reason = data["rejection_reason"]
        order.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(order)
        return jsonify(order.to_dict()), 200

    # Field modification (only allowed in modifiable states)
    if order.status not in MODIFIABLE_STATUSES:
        return jsonify({"error": f"Order in status {order.status} cannot be modified"}), 422

    allowed_fields = {"quantity", "price", "venue"}
    for field in allowed_fields:
        if field in data:
            setattr(order, field, data[field])

    order.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(order)
    return jsonify(order.to_dict()), 200


@orders_bp.delete("/<int:order_id>")
def cancel_order(order_id: int):
    db = _db()
    order = db.get(Order, order_id)
    if not order:
        return jsonify({"error": "Order not found"}), 404

    allowed = VALID_TRANSITIONS.get(order.status, set())
    if OrderStatus.CANCELLED not in allowed:
        return jsonify({"error": f"Cannot cancel order in status {order.status}"}), 422

    order.status = OrderStatus.CANCELLED
    order.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(order)
    return jsonify(order.to_dict()), 200
