from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import Column, DateTime, Integer, Numeric, String, Text
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class OrderStatus(str, Enum):
    NEW = "NEW"
    PENDING_ROUTING = "PENDING_ROUTING"
    ROUTED = "ROUTED"
    EXECUTED = "EXECUTED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"


VALID_TRANSITIONS: dict[str, set[str]] = {
    OrderStatus.NEW: {OrderStatus.PENDING_ROUTING, OrderStatus.CANCELLED, OrderStatus.REJECTED},
    OrderStatus.PENDING_ROUTING: {OrderStatus.ROUTED, OrderStatus.CANCELLED, OrderStatus.REJECTED},
    OrderStatus.ROUTED: {OrderStatus.EXECUTED, OrderStatus.CANCELLED, OrderStatus.REJECTED},
    OrderStatus.EXECUTED: set(),
    OrderStatus.CANCELLED: set(),
    OrderStatus.REJECTED: set(),
}

MODIFIABLE_STATUSES = {OrderStatus.NEW, OrderStatus.PENDING_ROUTING}


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, autoincrement=True)
    client_order_id = Column(String(64), unique=True, nullable=False)
    symbol = Column(String(16), nullable=False)
    side = Column(String(4), nullable=False)  # BUY / SELL
    quantity = Column(Numeric(18, 6), nullable=False)
    price = Column(Numeric(18, 6), nullable=True)
    order_type = Column(String(16), nullable=False)  # MARKET / LIMIT
    status = Column(String(32), nullable=False, default=OrderStatus.NEW)
    venue = Column(String(32), nullable=True)
    rejection_reason = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "client_order_id": self.client_order_id,
            "symbol": self.symbol,
            "side": self.side,
            "quantity": str(self.quantity),
            "price": str(self.price) if self.price is not None else None,
            "order_type": self.order_type,
            "status": self.status,
            "venue": self.venue,
            "rejection_reason": self.rejection_reason,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
