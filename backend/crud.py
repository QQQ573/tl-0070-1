from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import or_
import models
import schemas


def get_items(
    db: Session,
    page: int = 1,
    page_size: int = 10,
    series: str = None,
    rarity: str = None,
    keyword: str = None,
):
    query = db.query(models.Item).filter(models.Item.deleted_at.is_(None))
    if series:
        query = query.filter(models.Item.series == series)
    if rarity:
        query = query.filter(models.Item.rarity == rarity)
    if keyword:
        query = query.filter(
            or_(
                models.Item.name.contains(keyword),
                models.Item.style_id.contains(keyword),
                models.Item.series.contains(keyword),
            )
        )
    total = query.count()
    items = (
        query.order_by(models.Item.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return schemas.ItemPage(
        total=total, page=page, page_size=page_size, items=items
    )


def get_item(db: Session, item_id: int):
    return (
        db.query(models.Item)
        .filter(models.Item.id == item_id, models.Item.deleted_at.is_(None))
        .first()
    )


def create_item(db: Session, item: schemas.ItemCreate):
    db_item = models.Item(**item.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def update_item(db: Session, item_id: int, item: schemas.ItemUpdate):
    db_item = get_item(db, item_id)
    if not db_item:
        return None
    update_data = item.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_item, key, value)
    db_item.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_item)
    return db_item


def soft_delete_item(db: Session, item_id: int):
    db_item = get_item(db, item_id)
    if not db_item:
        return None
    db_item.deleted_at = datetime.utcnow()
    db.commit()
    db.refresh(db_item)
    return db_item


def get_exchanges(
    db: Session,
    page: int = 1,
    page_size: int = 10,
    counterparty: str = None,
):
    query = db.query(models.Exchange).filter(models.Exchange.deleted_at.is_(None))
    if counterparty:
        query = query.filter(models.Exchange.counterparty.contains(counterparty))
    total = query.count()
    exchanges = (
        query.order_by(models.Exchange.exchange_date.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    result = []
    for ex in exchanges:
        ex_out = schemas.ExchangeOut.model_validate(ex)
        if ex.item:
            ex_out.item_series = ex.item.series
            ex_out.item_name = ex.item.name
        result.append(ex_out)
    return schemas.ExchangePage(
        total=total, page=page, page_size=page_size, exchanges=result
    )


def get_exchange(db: Session, exchange_id: int):
    return (
        db.query(models.Exchange)
        .filter(
            models.Exchange.id == exchange_id, models.Exchange.deleted_at.is_(None)
        )
        .first()
    )


def create_exchange(db: Session, exchange: schemas.ExchangeCreate):
    db_exchange = models.Exchange(**exchange.model_dump())
    db.add(db_exchange)
    db.commit()
    db.refresh(db_exchange)
    return db_exchange


def update_exchange(db: Session, exchange_id: int, exchange: schemas.ExchangeUpdate):
    db_exchange = get_exchange(db, exchange_id)
    if not db_exchange:
        return None
    update_data = exchange.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_exchange, key, value)
    db_exchange.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_exchange)
    return db_exchange


def soft_delete_exchange(db: Session, exchange_id: int):
    db_exchange = get_exchange(db, exchange_id)
    if not db_exchange:
        return None
    db_exchange.deleted_at = datetime.utcnow()
    db.commit()
    db.refresh(db_exchange)
    return db_exchange


def get_all_series(db: Session):
    rows = (
        db.query(models.Item.series)
        .filter(models.Item.deleted_at.is_(None))
        .distinct()
        .all()
    )
    return [r[0] for r in rows]
