from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from database import Base


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    series = Column(String(100), nullable=False)
    style_id = Column(String(50), nullable=False)
    name = Column(String(200), nullable=False)
    rarity = Column(String(20), nullable=False)
    acquisition_method = Column(String(50), nullable=False)
    purchase_price = Column(Float, default=0.0)
    status = Column(String(20), nullable=False, default="在库")
    batch_no = Column(String(50), nullable=True)
    image_path = Column(String(500), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)

    exchanges = relationship("Exchange", back_populates="item")


class Exchange(Base):
    __tablename__ = "exchanges"

    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False)
    exchange_date = Column(String(20), nullable=False)
    counterparty = Column(String(100), nullable=False)
    price_difference = Column(Float, default=0.0)
    flow_status = Column(String(20), nullable=False, default="洽谈中")
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)

    item = relationship("Item", back_populates="exchanges")


class MarketPrice(Base):
    __tablename__ = "market_prices"
    __table_args__ = (
        UniqueConstraint("style_id", "platform", "record_date", name="uq_market_style_platform_date"),
    )

    id = Column(Integer, primary_key=True, index=True)
    style_id = Column(String(50), nullable=False, index=True)
    platform = Column(String(50), nullable=False)
    deal_price = Column(Float, nullable=False)
    record_date = Column(String(20), nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)
