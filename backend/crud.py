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
    item = get_item(db, exchange.item_id)
    if item and item.status == "在库":
        item.status = "置换中"
        item.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_exchange)
    return db_exchange


def update_exchange(db: Session, exchange_id: int, exchange: schemas.ExchangeUpdate):
    db_exchange = get_exchange(db, exchange_id)
    if not db_exchange:
        return None
    if db_exchange.flow_status in ("已成交", "已撤回"):
        raise ValueError("已完结的置换记录不可编辑")
    update_data = exchange.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_exchange, key, value)
    db_exchange.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_exchange)
    return db_exchange


def confirm_exchange(db: Session, exchange_id: int):
    db_exchange = get_exchange(db, exchange_id)
    if not db_exchange:
        return None
    if db_exchange.flow_status != "洽谈中":
        raise ValueError("仅洽谈中的置换可确认成交")
    db_exchange.flow_status = "已成交"
    db_exchange.updated_at = datetime.utcnow()
    item = get_item(db, db_exchange.item_id)
    if item:
        item.status = "已出"
        item.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_exchange)
    return db_exchange


def cancel_exchange(db: Session, exchange_id: int):
    db_exchange = get_exchange(db, exchange_id)
    if not db_exchange:
        return None
    if db_exchange.flow_status != "洽谈中":
        raise ValueError("仅洽谈中的置换可撤回")
    db_exchange.flow_status = "已撤回"
    db_exchange.updated_at = datetime.utcnow()
    item = get_item(db, db_exchange.item_id)
    if item and item.status == "置换中":
        item.status = "在库"
        item.updated_at = datetime.utcnow()
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


# ── 行情参考价 ──────────────────────────────────────────

def _market_query(db: Session, style_id: str = None, date_from: str = None, date_to: str = None):
    query = db.query(models.MarketPrice).filter(models.MarketPrice.deleted_at.is_(None))
    if style_id:
        query = query.filter(models.MarketPrice.style_id == style_id)
    if date_from:
        query = query.filter(models.MarketPrice.record_date >= date_from)
    if date_to:
        query = query.filter(models.MarketPrice.record_date <= date_to)
    return query


def get_market_prices(db: Session, page=1, page_size=10, style_id=None, date_from=None, date_to=None):
    query = _market_query(db, style_id, date_from, date_to)
    total = query.count()
    prices = (
        query.order_by(models.MarketPrice.record_date.desc(), models.MarketPrice.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return schemas.MarketPricePage(total=total, page=page, page_size=page_size, prices=prices)


def get_market_price(db: Session, price_id: int):
    return (
        db.query(models.MarketPrice)
        .filter(models.MarketPrice.id == price_id, models.MarketPrice.deleted_at.is_(None))
        .first()
    )


def _duplicate_market_price(db: Session, style_id: str, platform: str, record_date: str, exclude_id=None):
    query = db.query(models.MarketPrice).filter(
        models.MarketPrice.deleted_at.is_(None),
        models.MarketPrice.style_id == style_id,
        models.MarketPrice.platform == platform,
        models.MarketPrice.record_date == record_date,
    )
    if exclude_id:
        query = query.filter(models.MarketPrice.id != exclude_id)
    return query.first()


def create_market_price(db: Session, price: schemas.MarketPriceCreate):
    if _duplicate_market_price(db, price.style_id, price.platform, price.record_date):
        raise ValueError("同一款式、平台、日期已存在行情记录")
    db_price = models.MarketPrice(**price.model_dump())
    db.add(db_price)
    db.commit()
    db.refresh(db_price)
    return db_price


def update_market_price(db: Session, price_id: int, price: schemas.MarketPriceUpdate):
    db_price = get_market_price(db, price_id)
    if not db_price:
        return None
    data = price.model_dump(exclude_unset=True)
    style_id = data.get("style_id", db_price.style_id)
    platform = data.get("platform", db_price.platform)
    record_date = data.get("record_date", db_price.record_date)
    dup = _duplicate_market_price(db, style_id, platform, record_date, exclude_id=price_id)
    if dup:
        raise ValueError("同一款式、平台、日期已存在行情记录")
    for key, value in data.items():
        setattr(db_price, key, value)
    db_price.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_price)
    return db_price


def soft_delete_market_price(db: Session, price_id: int):
    db_price = get_market_price(db, price_id)
    if not db_price:
        return None
    db_price.deleted_at = datetime.utcnow()
    db.commit()
    db.refresh(db_price)
    return db_price


def get_market_trend(db: Session, style_id: str, limit: int = 10, purchase_price: float = None):
    records = (
        _market_query(db, style_id=style_id)
        .order_by(models.MarketPrice.record_date.asc())
        .limit(limit)
        .all()
    )
    latest = records[-1].deal_price if records else None
    diff_percent = None
    if latest is not None and purchase_price and purchase_price > 0:
        diff_percent = round((latest - purchase_price) / purchase_price * 100, 2)
    return schemas.MarketPriceTrend(
        style_id=style_id,
        records=records,
        latest_price=latest,
        purchase_price=purchase_price,
        diff_percent=diff_percent,
    )


# ── 资产看板统计 ──────────────────────────────────────────

def get_dashboard_stats(db: Session):
    items = db.query(models.Item).filter(models.Item.deleted_at.is_(None)).all()
    total_items = len(items)
    instock = [i for i in items if i.status == "在库"]
    out = [i for i in items if i.status == "已出"]
    exchanging = [i for i in items if i.status == "置换中"]
    hidden = [i for i in items if i.rarity == "隐藏"]

    series_map = {}
    for item in items:
        if item.series not in series_map:
            series_map[item.series] = {"count": 0, "total_value": 0.0}
        series_map[item.series]["count"] += 1
        series_map[item.series]["total_value"] += item.purchase_price or 0

    series_stats = [
        schemas.SeriesStat(series=k, count=v["count"], total_value=round(v["total_value"], 2))
        for k, v in sorted(series_map.items(), key=lambda x: -x[1]["count"])
    ]

    overview = schemas.OverviewStats(
        total_items=total_items,
        instock_count=len(instock),
        out_count=len(out),
        exchanging_count=len(exchanging),
        hidden_count=len(hidden),
        instock_value=round(sum(i.purchase_price or 0 for i in instock), 2),
        series_stats=series_stats,
    )

    exchanges = (
        db.query(models.Exchange)
        .filter(models.Exchange.deleted_at.is_(None), models.Exchange.flow_status == "已成交")
        .all()
    )
    month_counts = {}
    for ex in exchanges:
        month = ex.exchange_date[:7]
        month_counts[month] = month_counts.get(month, 0) + 1

    sorted_months = sorted(month_counts.keys())[-6:]
    monthly = [schemas.MonthlyExchangeStat(month=m, count=month_counts[m]) for m in sorted_months]

    return schemas.DashboardStats(overview=overview, monthly_exchanges=monthly)


# ── 回收站 ──────────────────────────────────────────

def get_recycle_bin(db: Session):
    deleted_items = (
        db.query(models.Item)
        .filter(models.Item.deleted_at.is_not(None))
        .order_by(models.Item.deleted_at.desc())
        .all()
    )
    deleted_exchanges = (
        db.query(models.Exchange)
        .filter(models.Exchange.deleted_at.is_not(None))
        .order_by(models.Exchange.deleted_at.desc())
        .all()
    )
    ex_list = []
    for ex in deleted_exchanges:
        ex_out = schemas.RecycleExchangeOut.model_validate(ex)
        if ex.item:
            ex_out.item_series = ex.item.series
            ex_out.item_name = ex.item.name
        ex_list.append(ex_out)
    return schemas.RecyclePage(
        items=[schemas.RecycleItemOut.model_validate(i) for i in deleted_items],
        exchanges=ex_list,
    )


def restore_item(db: Session, item_id: int):
    db_item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if not db_item or db_item.deleted_at is None:
        return None
    db_item.deleted_at = None
    db_item.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_item)
    return db_item


def restore_exchange(db: Session, exchange_id: int):
    db_exchange = db.query(models.Exchange).filter(models.Exchange.id == exchange_id).first()
    if not db_exchange or db_exchange.deleted_at is None:
        return None
    db_exchange.deleted_at = None
    db_exchange.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_exchange)
    return db_exchange


def hard_delete_item(db: Session, item_id: int):
    db_item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if not db_item or db_item.deleted_at is None:
        return False
    db.delete(db_item)
    db.commit()
    return True


def hard_delete_exchange(db: Session, exchange_id: int):
    db_exchange = db.query(models.Exchange).filter(models.Exchange.id == exchange_id).first()
    if not db_exchange or db_exchange.deleted_at is None:
        return False
    db.delete(db_exchange)
    db.commit()
    return True
